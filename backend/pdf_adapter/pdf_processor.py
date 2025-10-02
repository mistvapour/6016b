"""
PDF处理器主模块
整合所有PDF处理功能，提供统一的处理接口
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json

from .extract_tables import TableExtractor, extract_tables_from_pdf
from .parse_sections import SectionParser, parse_6016_sections
from .normalize_bits import FieldNormalizer, normalize_pdf_data, validate_extracted_data
from .build_sim import SIMBuilder, build_sim_from_pdf_data, export_sim_to_yaml
from .validators import ComprehensiveValidator, validate_pdf_extraction, generate_validation_report

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF处理器主类"""
    
    def __init__(self, standard: str = "MIL-STD-6016", edition: str = "B"):
        self.standard = standard
        self.edition = edition
        self.table_extractor = TableExtractor()
        self.section_parser = SectionParser()
        self.field_normalizer = FieldNormalizer()
        self.validator = ComprehensiveValidator()
    
    def process_pdf(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        处理PDF文件，执行完整的提取和转换流程
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果为None则使用PDF文件所在目录
        
        Returns:
            处理结果字典
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if output_dir is None:
                output_dir = pdf_path.parent
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Processing PDF: {pdf_path}")
            
            # 1. 提取表格
            logger.info("Step 1: Extracting tables...")
            tables_by_page = extract_tables_from_pdf(str(pdf_path))
            
            # 2. 解析章节
            logger.info("Step 2: Parsing sections...")
            sections = parse_6016_sections(str(pdf_path))
            
            # 3. 标准化数据
            logger.info("Step 3: Normalizing data...")
            normalized_data = self._normalize_extracted_data(tables_by_page, sections)
            
            # 4. 构建SIM
            logger.info("Step 4: Building SIM...")
            sim = self._build_sim_from_data(normalized_data)
            
            # 5. 校验数据
            logger.info("Step 5: Validating data...")
            validation_result = self.validator.validate_sim(sim.__dict__)
            
            # 6. 导出YAML
            logger.info("Step 6: Exporting YAML...")
            yaml_files = export_sim_to_yaml(sim, str(output_dir))
            
            # 7. 生成报告
            logger.info("Step 7: Generating report...")
            report = self._generate_processing_report(
                pdf_path, sim, validation_result, yaml_files
            )
            
            # 保存报告
            report_path = output_dir / f"{pdf_path.stem}_processing_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'pdf_path': str(pdf_path),
                'output_dir': str(output_dir),
                'sim': sim.__dict__,
                'validation_result': {
                    'valid': validation_result.valid,
                    'errors': [e.__dict__ for e in validation_result.errors],
                    'warnings': [w.__dict__ for w in validation_result.warnings],
                    'coverage': validation_result.coverage,
                    'confidence': validation_result.confidence
                },
                'yaml_files': list(yaml_files.keys()),
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'pdf_path': str(pdf_path)
            }
    
    def _normalize_extracted_data(self, tables_by_page: Dict[int, List[Dict[str, Any]]], 
                                sections: Dict[str, List[Any]]) -> Dict[str, Any]:
        """标准化提取的数据"""
        normalized = {
            'j_messages': [],
            'appendix_b': [],
            'tables': tables_by_page
        }
        
        # 处理J消息章节
        for section in sections.get('j_messages', []):
            # 查找相关表格
            related_tables = self._find_related_tables(section, tables_by_page)
            
            # 提取字段数据
            fields = self._extract_fields_from_tables(related_tables)
            
            # 标准化字段
            normalized_fields = normalize_pdf_data(fields)
            
            normalized['j_messages'].append({
                'label': section.label,
                'title': section.title,
                'start_page': section.start_page,
                'fields': normalized_fields
            })
        
        # 处理Appendix B章节
        for section in sections.get('appendix_b', []):
            # 解析DFI/DUI/DI信息
            dfiduidi_data = self._parse_appendix_section(section)
            
            normalized['appendix_b'].append(dfiduidi_data)
        
        return normalized
    
    def _find_related_tables(self, section, tables_by_page: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """查找与章节相关的表格"""
        related_tables = []
        start_page = section.start_page
        
        # 在章节开始页面的后续几页中查找表格
        for page_num in range(start_page, start_page + 3):
            if page_num in tables_by_page:
                related_tables.extend(tables_by_page[page_num])
        
        return related_tables
    
    def _extract_fields_from_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从表格中提取字段数据"""
        fields = []
        
        for table in tables:
            data = table.get('data', [])
            if not data:
                continue
            
            # 查找包含位段信息的行
            for row in data:
                if self._is_field_row(row):
                    field_data = self._parse_field_row(row)
                    if field_data:
                        fields.append(field_data)
        
        return fields
    
    def _is_field_row(self, row: Dict[str, Any]) -> bool:
        """判断是否是字段行"""
        # 检查是否包含位段信息
        bit_fields = ['bit', 'start', 'end', 'bits']
        for field in bit_fields:
            if field in row and row[field]:
                # 检查是否包含位段模式
                import re
                bit_pattern = re.compile(r'\d+\s*[-–~\.]{1,2}\s*\d+')
                if bit_pattern.search(str(row[field])):
                    return True
        return False
    
    def _parse_field_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析字段行"""
        try:
            field_data = {}
            
            # 提取字段名
            if 'field' in row:
                field_data['field'] = row['field']
            elif 'field_name' in row:
                field_data['field'] = row['field_name']
            
            # 提取位段信息
            bit_fields = ['bit', 'start', 'end', 'bits']
            for field in bit_fields:
                if field in row and row[field]:
                    field_data[field] = row[field]
                    break
            
            # 提取描述
            if 'description' in row:
                field_data['description'] = row['description']
            
            # 提取其他信息
            for key, value in row.items():
                if key not in ['field', 'field_name', 'bit', 'start', 'end', 'bits', 'description']:
                    field_data[key] = value
            
            return field_data if field_data else None
            
        except Exception as e:
            logger.error(f"Failed to parse field row: {e}")
            return None
    
    def _parse_appendix_section(self, section) -> Dict[str, Any]:
        """解析Appendix B章节"""
        # 这里需要根据实际的Appendix B格式来解析
        # 暂时返回基本结构
        return {
            'dfi': {
                'num': 0,
                'name': section.title,
                'description': section.content
            },
            'dui': [],
            'di': []
        }
    
    def _build_sim_from_data(self, normalized_data: Dict[str, Any]) -> Any:
        """从标准化数据构建SIM"""
        return build_sim_from_pdf_data(
            normalized_data['j_messages'],
            normalized_data['appendix_b'],
            self.standard,
            self.edition
        )
    
    def _generate_processing_report(self, pdf_path: Path, sim: Any, 
                                  validation_result: Any, yaml_files: Dict[str, str]) -> Dict[str, Any]:
        """生成处理报告"""
        from datetime import datetime
        
        return {
            'pdf_file': str(pdf_path),
            'processing_time': datetime.now().isoformat(),
            'standard': self.standard,
            'edition': self.edition,
            'statistics': {
                'j_messages_count': len(sim.j_messages),
                'dfiduidi_count': len(sim.dfi_dui_di),
                'enums_count': len(sim.enums),
                'units_count': len(sim.units)
            },
            'validation': {
                'valid': validation_result.valid,
                'error_count': len(validation_result.errors),
                'warning_count': len(validation_result.warnings),
                'coverage': validation_result.coverage,
                'confidence': validation_result.confidence
            },
            'output_files': list(yaml_files.keys()),
            'validation_report': generate_validation_report(validation_result)
        }

def process_pdf_file(pdf_path: str, output_dir: Optional[str] = None, 
                    standard: str = "MIL-STD-6016", edition: str = "B") -> Dict[str, Any]:
    """
    处理单个PDF文件的便捷函数
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        standard: 标准名称
        edition: 版本
    
    Returns:
        处理结果
    """
    processor = PDFProcessor(standard, edition)
    return processor.process_pdf(pdf_path, output_dir)

def batch_process_pdfs(pdf_dir: str, output_dir: Optional[str] = None,
                      standard: str = "MIL-STD-6016", edition: str = "B") -> List[Dict[str, Any]]:
    """
    批量处理PDF文件
    
    Args:
        pdf_dir: PDF文件目录
        output_dir: 输出目录
        standard: 标准名称
        edition: 版本
    
    Returns:
        处理结果列表
    """
    pdf_dir = Path(pdf_dir)
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_dir}")
        return []
    
    results = []
    processor = PDFProcessor(standard, edition)
    
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file.name}...")
        result = processor.process_pdf(str(pdf_file), output_dir)
        results.append(result)
    
    return results
