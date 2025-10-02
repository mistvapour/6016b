"""
PDF表格提取模块
支持Camelot和pdfplumber双路抽取，自动选择最佳结果
"""
import camelot
import pdfplumber
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class TableExtractionResult:
    """表格提取结果"""
    data: List[List[str]]
    confidence: float
    method: str
    page: int
    bbox: Optional[Tuple[float, float, float, float]] = None
    source_ref: Optional[str] = None

class TableExtractor:
    """PDF表格提取器"""
    
    def __init__(self):
        # 6016标准的关键列头模式
        self.column_patterns = {
            'word': re.compile(r'^word\s*$', re.I),
            'bit': re.compile(r'^bit(s?)\s*$', re.I),
            'start': re.compile(r'^start\s*$', re.I),
            'end': re.compile(r'^end\s*$', re.I),
            'field': re.compile(r'^field\s*$', re.I),
            'description': re.compile(r'^description\s*$', re.I),
            'resolution': re.compile(r'^resolution\s*$', re.I),
            'units': re.compile(r'^unit(s?)\s*$', re.I)
        }
        
        # 位段范围模式
        self.bit_range_pattern = re.compile(r'(?P<start>\d+)\s*[-–~\.]{1,2}\s*(?P<end>\d+)')
        
    def extract_tables(self, pdf_path: str, page: int) -> List[TableExtractionResult]:
        """
        从PDF页面提取表格
        使用Camelot和pdfplumber双路并跑，选择最佳结果
        """
        results = []
        
        # 1. Camelot lattice模式（有网格线的表格）
        try:
            lattice_tables = camelot.read_pdf(
                pdf_path, 
                pages=str(page), 
                flavor="lattice",
                line_scale=40
            )
            for table in lattice_tables:
                if len(table.df) > 1:  # 至少要有表头和数据行
                    result = self._process_camelot_table(table, page, "lattice")
                    if result:
                        results.append(result)
        except Exception as e:
            logger.warning(f"Camelot lattice failed for page {page}: {e}")
        
        # 2. Camelot stream模式（按列对齐的表格）
        try:
            stream_tables = camelot.read_pdf(
                pdf_path, 
                pages=str(page), 
                flavor="stream",
                edge_tol=500
            )
            for table in stream_tables:
                if len(table.df) > 1:
                    result = self._process_camelot_table(table, page, "stream")
                    if result:
                        results.append(result)
        except Exception as e:
            logger.warning(f"Camelot stream failed for page {page}: {e}")
        
        # 3. pdfplumber作为备选
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page <= len(pdf.pages):
                    plumber_tables = pdf.pages[page-1].extract_tables()
                    for i, table in enumerate(plumber_tables):
                        if table and len(table) > 1:
                            result = self._process_plumber_table(table, page, i)
                            if result:
                                results.append(result)
        except Exception as e:
            logger.warning(f"pdfplumber failed for page {page}: {e}")
        
        # 4. 选择最佳结果
        if results:
            best_result = self._select_best_table(results)
            return [best_result]
        
        return []
    
    def _process_camelot_table(self, table, page: int, method: str) -> Optional[TableExtractionResult]:
        """处理Camelot提取的表格"""
        try:
            df = table.df
            data = df.values.tolist()
            
            # 计算置信度
            confidence = self._calculate_confidence(data, method)
            
            return TableExtractionResult(
                data=data,
                confidence=confidence,
                method=f"camelot_{method}",
                page=page,
                bbox=table._bbox if hasattr(table, '_bbox') else None
            )
        except Exception as e:
            logger.error(f"Error processing camelot table: {e}")
            return None
    
    def _process_plumber_table(self, table: List[List[str]], page: int, table_idx: int) -> Optional[TableExtractionResult]:
        """处理pdfplumber提取的表格"""
        try:
            # 清理数据
            cleaned_data = []
            for row in table:
                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                cleaned_data.append(cleaned_row)
            
            # 计算置信度
            confidence = self._calculate_confidence(cleaned_data, "plumber")
            
            return TableExtractionResult(
                data=cleaned_data,
                confidence=confidence,
                method="pdfplumber",
                page=page,
                source_ref=f"table_{table_idx}"
            )
        except Exception as e:
            logger.error(f"Error processing plumber table: {e}")
            return None
    
    def _calculate_confidence(self, data: List[List[str]], method: str) -> float:
        """计算表格提取的置信度"""
        if not data or len(data) < 2:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        # 1. 列头匹配度 (40%)
        header_score = self._score_headers(data[0])
        score += header_score * 0.4
        max_score += 0.4
        
        # 2. 列数一致性 (20%)
        col_consistency = self._score_column_consistency(data)
        score += col_consistency * 0.2
        max_score += 0.2
        
        # 3. 位段可解析性 (30%)
        bit_parse_score = self._score_bit_parsability(data)
        score += bit_parse_score * 0.3
        max_score += 0.3
        
        # 4. 方法特定加分 (10%)
        method_bonus = self._get_method_bonus(method)
        score += method_bonus * 0.1
        max_score += 0.1
        
        return min(score / max_score, 1.0) if max_score > 0 else 0.0
    
    def _score_headers(self, header_row: List[str]) -> float:
        """评分表头匹配度"""
        if not header_row:
            return 0.0
        
        matches = 0
        total = len(header_row)
        
        for cell in header_row:
            cell_clean = str(cell).strip().lower()
            for pattern_name, pattern in self.column_patterns.items():
                if pattern.search(cell_clean):
                    matches += 1
                    break
        
        return matches / total if total > 0 else 0.0
    
    def _score_column_consistency(self, data: List[List[str]]) -> float:
        """评分列数一致性"""
        if len(data) < 2:
            return 0.0
        
        first_row_len = len(data[0])
        consistent_rows = sum(1 for row in data if len(row) == first_row_len)
        
        return consistent_rows / len(data)
    
    def _score_bit_parsability(self, data: List[List[str]]) -> float:
        """评分位段可解析性"""
        if len(data) < 2:
            return 0.0
        
        # 寻找位段列
        bit_columns = []
        for i, cell in enumerate(data[0]):
            cell_clean = str(cell).strip().lower()
            if any(pattern.search(cell_clean) for pattern in [self.column_patterns['bit'], 
                                                             self.column_patterns['start'], 
                                                             self.column_patterns['end']]):
                bit_columns.append(i)
        
        if not bit_columns:
            return 0.0
        
        # 检查数据行中的位段格式
        parseable_rows = 0
        for row in data[1:]:  # 跳过表头
            for col_idx in bit_columns:
                if col_idx < len(row):
                    cell = str(row[col_idx]).strip()
                    if self.bit_range_pattern.search(cell):
                        parseable_rows += 1
                        break
        
        return parseable_rows / (len(data) - 1) if len(data) > 1 else 0.0
    
    def _get_method_bonus(self, method: str) -> float:
        """获取方法特定加分"""
        bonuses = {
            "camelot_lattice": 0.8,  # 网格线表格通常更准确
            "camelot_stream": 0.6,   # 流式表格中等准确度
            "pdfplumber": 0.4        # 备选方案
        }
        return bonuses.get(method, 0.0)
    
    def _select_best_table(self, results: List[TableExtractionResult]) -> TableExtractionResult:
        """选择最佳表格提取结果"""
        if not results:
            return None
        
        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        # 如果最高置信度相同，优先选择Camelot lattice
        best_confidence = results[0].confidence
        best_results = [r for r in results if r.confidence == best_confidence]
        
        if len(best_results) > 1:
            # 优先选择lattice方法
            lattice_results = [r for r in best_results if r.method == "camelot_lattice"]
            if lattice_results:
                return lattice_results[0]
        
        return results[0]
    
    def normalize_table_data(self, result: TableExtractionResult) -> Dict[str, Any]:
        """标准化表格数据为字典格式"""
        if not result.data or len(result.data) < 2:
            return {}
        
        headers = [str(cell).strip() for cell in result.data[0]]
        rows = result.data[1:]
        
        # 标准化列名
        normalized_headers = []
        for header in headers:
            header_lower = header.lower()
            if self.column_patterns['word'].search(header_lower):
                normalized_headers.append('word')
            elif self.column_patterns['bit'].search(header_lower):
                normalized_headers.append('bit')
            elif self.column_patterns['start'].search(header_lower):
                normalized_headers.append('start')
            elif self.column_patterns['end'].search(header_lower):
                normalized_headers.append('end')
            elif self.column_patterns['field'].search(header_lower):
                normalized_headers.append('field')
            elif self.column_patterns['description'].search(header_lower):
                normalized_headers.append('description')
            elif self.column_patterns['resolution'].search(header_lower):
                normalized_headers.append('resolution')
            elif self.column_patterns['units'].search(header_lower):
                normalized_headers.append('units')
            else:
                normalized_headers.append(header)
        
        # 转换为字典列表
        normalized_data = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(normalized_headers):
                    row_dict[normalized_headers[i]] = str(value).strip()
            normalized_data.append(row_dict)
        
        return {
            'headers': normalized_headers,
            'data': normalized_data,
            'confidence': result.confidence,
            'method': result.method,
            'page': result.page,
            'bbox': result.bbox,
            'source_ref': result.source_ref
        }

def extract_tables_from_pdf(pdf_path: str, pages: Optional[List[int]] = None) -> Dict[int, List[Dict[str, Any]]]:
    """
    从PDF文件提取所有表格
    Args:
        pdf_path: PDF文件路径
        pages: 要处理的页面列表，None表示处理所有页面
    Returns:
        字典，键为页面号，值为该页面的表格列表
    """
    extractor = TableExtractor()
    results = {}
    
    if pages is None:
        # 获取总页数
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = list(range(1, len(pdf.pages) + 1))
        except Exception as e:
            logger.error(f"Failed to get page count: {e}")
            return results
    
    for page in pages:
        try:
            tables = extractor.extract_tables(pdf_path, page)
            if tables:
                normalized_tables = []
                for table in tables:
                    normalized = extractor.normalize_table_data(table)
                    if normalized:
                        normalized_tables.append(normalized)
                results[page] = normalized_tables
        except Exception as e:
            logger.error(f"Failed to extract tables from page {page}: {e}")
    
    return results
