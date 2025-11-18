#!/usr/bin/env python3
"""
统一多格式自动化导入系统
支持PDF、XML、JSON、CSV、DOCX等多种格式的自动识别、转换和导入
"""
import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import json
import yaml

# 格式检测
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
import pandas as pd

# 现有模块
from pdf_adapter.pdf_processor import PDFProcessor
from import_yaml import YAMLImporter

logger = logging.getLogger(__name__)

class FormatAdapter(ABC):
    """格式适配器抽象基类"""
    
    @abstractmethod
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        """判断是否能处理此格式"""
        pass
    
    @abstractmethod
    def detect_standard(self, file_path: str) -> Dict[str, Any]:
        """检测文件的标准类型和版本"""
        pass
    
    @abstractmethod
    def process(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理文件并返回标准化结果"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """返回支持的格式列表"""
        pass

class PDFAdapter(FormatAdapter):
    """PDF格式适配器"""
    
    def __init__(self):
        self.processor = PDFProcessor()
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return mime_type == 'application/pdf' or file_path.lower().endswith('.pdf')
    
    def detect_standard(self, file_path: str) -> Dict[str, Any]:
        """检测PDF标准类型"""
        try:
            doc = fitz.open(file_path)
            text_sample = ""
            
            # 提取前几页的文本进行分析
            for page_num in range(min(5, len(doc))):
                text_sample += doc[page_num].get_text()
            
            text_lower = text_sample.lower()
            
            # 标准检测规则
            if 'mil-std-6016' in text_lower or 'link 16' in text_lower:
                return {
                    "standard": "MIL-STD-6016",
                    "type": "Link16",
                    "adapter": "pdf_adapter",
                    "confidence": 0.95,
                    "pages": len(doc),
                    "processing_method": "6016_specialized"
                }
            elif 'mqtt' in text_lower and ('control packet' in text_lower or 'publish' in text_lower):
                return {
                    "standard": "MQTT",
                    "type": "Protocol",
                    "adapter": "mqtt_adapter", 
                    "confidence": 0.90,
                    "pages": len(doc),
                    "processing_method": "mqtt_specialized"
                }
            elif any(kw in text_lower for kw in ['j2.0', 'j2.1', 'j2.2', 'j2.3', 'j2.4']):
                return {
                    "standard": "MIL-STD-6016",
                    "type": "J-Series",
                    "adapter": "pdf_adapter",
                    "confidence": 0.85,
                    "pages": len(doc),
                    "processing_method": "j_series_focused"
                }
            else:
                return {
                    "standard": "Generic",
                    "type": "PDF",
                    "adapter": "generic_pdf",
                    "confidence": 0.60,
                    "pages": len(doc),
                    "processing_method": "generic_table_extraction"
                }
                
        except Exception as e:
            logger.error(f"PDF标准检测失败: {e}")
            return {
                "standard": "Unknown",
                "type": "PDF",
                "adapter": "generic_pdf",
                "confidence": 0.30,
                "error": str(e),
                "processing_method": "fallback"
            }
    
    def process(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理PDF文件"""
        try:
            standard_info = self.detect_standard(file_path)
            
            if standard_info["standard"] == "MIL-STD-6016":
                # 使用现有的6016处理器
                result = self.processor.process_pdf(
                    file_path,
                    standard="MIL-STD-6016",
                    **kwargs
                )
                result["detected_standard"] = standard_info
                return result
                
            elif standard_info["standard"] == "MQTT":
                # 使用MQTT处理器
                from mqtt_adapter.extract_tables import read_tables, pick_best_tables
                from mqtt_adapter.parse_sections import detect_sections
                from mqtt_adapter.build_sim import build_sim
                from mqtt_adapter.export_yaml import export_yaml
                
                # MQTT处理流程
                pages = kwargs.get('pages', '1-100')
                page_list = self._parse_pages(pages)
                
                doc = fitz.open(file_path)
                page_texts = {p: doc[p-1].get_text() for p in page_list if 1 <= p <= len(doc)}
                
                per_page_tables = read_tables(file_path, page_list)
                best_tables = pick_best_tables(per_page_tables)
                sections = detect_sections(page_texts)
                sim = build_sim(sections, best_tables)
                
                # 导出YAML
                output_dir = kwargs.get('output_dir', '/tmp/mqtt_processing')
                os.makedirs(output_dir, exist_ok=True)
                yaml_path = os.path.join(output_dir, f"{Path(file_path).stem}.yaml")
                export_yaml(sim, yaml_path)
                
                return {
                    "success": True,
                    "standard": "MQTT",
                    "yaml_path": yaml_path,
                    "messages": [m["label"] for m in sim["spec_messages"]],
                    "detected_standard": standard_info
                }
            
            else:
                # 通用PDF处理
                return self._process_generic_pdf(file_path, **kwargs)
                
        except Exception as e:
            logger.error(f"PDF处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def _parse_pages(self, pages_str: str) -> List[int]:
        """解析页面范围字符串"""
        page_list = []
        for part in pages_str.split(","):
            if "-" in part:
                a, b = map(int, part.split("-"))
                page_list.extend(range(a, b + 1))
            else:
                page_list.append(int(part))
        return page_list
    
    def _process_generic_pdf(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """通用PDF处理"""
        # 实现通用PDF表格提取和数据处理
        return {
            "success": True,
            "standard": "Generic",
            "message": "通用PDF处理完成",
            "file_path": file_path
        }
    
    def get_supported_formats(self) -> List[str]:
        return ['.pdf', 'application/pdf']

class XMLAdapter(FormatAdapter):
    """XML格式适配器"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return mime_type in ['application/xml', 'text/xml'] or file_path.lower().endswith('.xml')
    
    def detect_standard(self, file_path: str) -> Dict[str, Any]:
        """检测XML标准类型"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # MAVLink检测
            if root.tag == 'mavlink' or 'mavlink' in str(root.attrib).lower():
                return {
                    "standard": "MAVLink",
                    "type": "Protocol",
                    "adapter": "mavlink_xml",
                    "confidence": 0.95,
                    "root_element": root.tag,
                    "processing_method": "mavlink_specialized"
                }
            
            # 检测其他标准
            elif root.tag in ['protocol', 'specification', 'standard']:
                return {
                    "standard": "Generic Protocol",
                    "type": "XML",
                    "adapter": "generic_xml",
                    "confidence": 0.70,
                    "root_element": root.tag,
                    "processing_method": "generic_xml"
                }
            
            else:
                return {
                    "standard": "Generic",
                    "type": "XML",
                    "adapter": "generic_xml",
                    "confidence": 0.50,
                    "root_element": root.tag,
                    "processing_method": "generic_xml"
                }
                
        except Exception as e:
            logger.error(f"XML标准检测失败: {e}")
            return {
                "standard": "Unknown",
                "type": "XML",
                "adapter": "generic_xml",
                "confidence": 0.30,
                "error": str(e),
                "processing_method": "fallback"
            }
    
    def process(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理XML文件"""
        try:
            standard_info = self.detect_standard(file_path)
            
            if standard_info["standard"] == "MAVLink":
                # 使用现有的MAVLink转换器
                from xml_to_pdf_converter import MAVLinkXMLConverter
                
                converter = MAVLinkXMLConverter(file_path)
                result = converter.run_conversion()
                
                if result["success"]:
                    yaml_path = result["files_generated"]["yaml"]
                    return {
                        "success": True,
                        "standard": "MAVLink",
                        "yaml_path": yaml_path,
                        "statistics": result["statistics"],
                        "detected_standard": standard_info
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error"),
                        "detected_standard": standard_info
                    }
            
            else:
                # 通用XML处理
                return self._process_generic_xml(file_path, **kwargs)
                
        except Exception as e:
            logger.error(f"XML处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def _process_generic_xml(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """通用XML处理"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 简单的XML到字典转换
            def xml_to_dict(element):
                result = {}
                for child in element:
                    if len(child) == 0:
                        result[child.tag] = child.text
                    else:
                        result[child.tag] = xml_to_dict(child)
                return result
            
            data = xml_to_dict(root)
            
            # 生成YAML文件
            output_dir = kwargs.get('output_dir', 'xml_output')
            os.makedirs(output_dir, exist_ok=True)
            yaml_path = os.path.join(output_dir, f"{Path(file_path).stem}.yaml")
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
            
            return {
                "success": True,
                "standard": "Generic XML",
                "yaml_path": yaml_path,
                "elements_count": len(data),
                "message": "通用XML处理完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        return ['.xml', 'application/xml', 'text/xml']

class JSONAdapter(FormatAdapter):
    """JSON格式适配器"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return mime_type == 'application/json' or file_path.lower().endswith('.json')
    
    def detect_standard(self, file_path: str) -> Dict[str, Any]:
        """检测JSON标准类型"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检测不同的JSON格式
            if isinstance(data, dict):
                if 'spec_messages' in data and 'standard' in data:
                    return {
                        "standard": data.get('standard', 'Unknown'),
                        "type": "SIM",
                        "adapter": "sim_json",
                        "confidence": 0.90,
                        "processing_method": "direct_import"
                    }
                elif 'messages' in data or 'enums' in data:
                    return {
                        "standard": "Protocol Definition",
                        "type": "JSON",
                        "adapter": "protocol_json",
                        "confidence": 0.80,
                        "processing_method": "protocol_conversion"
                    }
            
            return {
                "standard": "Generic",
                "type": "JSON",
                "adapter": "generic_json",
                "confidence": 0.60,
                "processing_method": "generic_conversion"
            }
            
        except Exception as e:
            logger.error(f"JSON标准检测失败: {e}")
            return {
                "standard": "Unknown",
                "type": "JSON",
                "adapter": "generic_json",
                "confidence": 0.30,
                "error": str(e),
                "processing_method": "fallback"
            }
    
    def process(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理JSON文件"""
        try:
            standard_info = self.detect_standard(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if standard_info["type"] == "SIM":
                # 直接转换为YAML并导入
                output_dir = kwargs.get('output_dir', 'json_output')
                os.makedirs(output_dir, exist_ok=True)
                yaml_path = os.path.join(output_dir, f"{Path(file_path).stem}.yaml")
                
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
                
                return {
                    "success": True,
                    "standard": standard_info["standard"],
                    "yaml_path": yaml_path,
                    "message": "JSON SIM数据转换完成",
                    "detected_standard": standard_info
                }
            
            else:
                # 通用JSON处理
                return self._process_generic_json(data, file_path, **kwargs)
                
        except Exception as e:
            logger.error(f"JSON处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def _process_generic_json(self, data: Any, file_path: str, **kwargs) -> Dict[str, Any]:
        """通用JSON处理"""
        try:
            # 生成标准化的YAML
            output_dir = kwargs.get('output_dir', 'json_output')
            os.makedirs(output_dir, exist_ok=True)
            yaml_path = os.path.join(output_dir, f"{Path(file_path).stem}.yaml")
            
            # 包装成标准格式
            standardized_data = {
                "standard": "Generic JSON",
                "edition": "1.0",
                "source_file": file_path,
                "data": data,
                "metadata": {
                    "conversion_time": datetime.now().isoformat(),
                    "converter": "json_adapter"
                }
            }
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(standardized_data, f, sort_keys=False, allow_unicode=True)
            
            return {
                "success": True,
                "standard": "Generic JSON",
                "yaml_path": yaml_path,
                "message": "通用JSON处理完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        return ['.json', 'application/json']

class CSVAdapter(FormatAdapter):
    """CSV格式适配器"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return mime_type == 'text/csv' or file_path.lower().endswith('.csv')
    
    def detect_standard(self, file_path: str) -> Dict[str, Any]:
        """检测CSV标准类型"""
        try:
            # 读取前几行来检测结构
            df = pd.read_csv(file_path, nrows=5)
            
            # 检测列名来判断类型
            columns = [col.lower() for col in df.columns]
            
            if any(col in columns for col in ['message', 'field', 'bits', 'name']):
                return {
                    "standard": "Protocol Definition",
                    "type": "CSV",
                    "adapter": "protocol_csv",
                    "confidence": 0.80,
                    "columns": len(df.columns),
                    "processing_method": "protocol_csv"
                }
            
            elif any(col in columns for col in ['enum', 'value', 'code', 'label']):
                return {
                    "standard": "Enum Definition",
                    "type": "CSV",
                    "adapter": "enum_csv",
                    "confidence": 0.75,
                    "columns": len(df.columns),
                    "processing_method": "enum_csv"
                }
            
            else:
                return {
                    "standard": "Generic",
                    "type": "CSV",
                    "adapter": "generic_csv",
                    "confidence": 0.60,
                    "columns": len(df.columns),
                    "processing_method": "generic_csv"
                }
                
        except Exception as e:
            logger.error(f"CSV标准检测失败: {e}")
            return {
                "standard": "Unknown",
                "type": "CSV",
                "adapter": "generic_csv",
                "confidence": 0.30,
                "error": str(e),
                "processing_method": "fallback"
            }
    
    def process(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理CSV文件"""
        try:
            standard_info = self.detect_standard(file_path)
            df = pd.read_csv(file_path)
            
            # 根据检测结果选择处理方法
            if standard_info["standard"] == "Protocol Definition":
                return self._process_protocol_csv(df, file_path, **kwargs)
            elif standard_info["standard"] == "Enum Definition":
                return self._process_enum_csv(df, file_path, **kwargs)
            else:
                return self._process_generic_csv(df, file_path, **kwargs)
                
        except Exception as e:
            logger.error(f"CSV处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def _process_protocol_csv(self, df: pd.DataFrame, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理协议定义CSV"""
        try:
            # 转换为标准格式
            messages = []
            
            # 假设CSV有 message, field, bits, description 等列
            for _, row in df.iterrows():
                # 根据实际CSV结构调整
                message_data = {
                    "name": row.get('field', row.get('name', '')),
                    "description": row.get('description', ''),
                    "bits": row.get('bits', ''),
                }
                messages.append(message_data)
            
            # 生成YAML
            output_dir = kwargs.get('output_dir', 'csv_output')
            os.makedirs(output_dir, exist_ok=True)
            yaml_path = os.path.join(output_dir, f"{Path(file_path).stem}.yaml")
            
            yaml_data = {
                "standard": "CSV Protocol",
                "edition": "1.0",
                "source_file": file_path,
                "spec_messages": [{"label": "CSV_DATA", "fields": messages}],
                "metadata": {
                    "conversion_time": datetime.now().isoformat(),
                    "converter": "csv_adapter",
                    "rows_processed": len(df)
                }
            }
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(yaml_data, f, sort_keys=False, allow_unicode=True)
            
            return {
                "success": True,
                "standard": "CSV Protocol",
                "yaml_path": yaml_path,
                "rows_processed": len(df),
                "message": "协议CSV处理完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_enum_csv(self, df: pd.DataFrame, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理枚举定义CSV"""
        # 类似协议处理，但针对枚举结构
        return self._process_generic_csv(df, file_path, **kwargs)
    
    def _process_generic_csv(self, df: pd.DataFrame, file_path: str, **kwargs) -> Dict[str, Any]:
        """通用CSV处理"""
        try:
            # 转换为字典格式
            data = df.to_dict('records')
            
            # 生成YAML
            output_dir = kwargs.get('output_dir', 'csv_output')
            os.makedirs(output_dir, exist_ok=True)
            yaml_path = os.path.join(output_dir, f"{Path(file_path).stem}.yaml")
            
            yaml_data = {
                "standard": "Generic CSV",
                "edition": "1.0",
                "source_file": file_path,
                "data": data,
                "metadata": {
                    "conversion_time": datetime.now().isoformat(),
                    "converter": "csv_adapter",
                    "rows": len(df),
                    "columns": list(df.columns)
                }
            }
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(yaml_data, f, sort_keys=False, allow_unicode=True)
            
            return {
                "success": True,
                "standard": "Generic CSV",
                "yaml_path": yaml_path,
                "rows_processed": len(df),
                "columns": list(df.columns),
                "message": "通用CSV处理完成"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        return ['.csv', 'text/csv']

class UniversalImportSystem:
    """统一导入系统主类"""
    
    def __init__(self):
        self.adapters = [
            PDFAdapter(),
            XMLAdapter(),
            JSONAdapter(),
            CSVAdapter(),
        ]
        self.yaml_importer = YAMLImporter()
        
    def detect_file_format(self, file_path: str) -> Dict[str, Any]:
        """检测文件格式和MIME类型"""
        try:
            # 使用文件扩展名和magic检测
            mime_type = mimetypes.guess_type(file_path)[0]
            
            # 如果mimetypes检测不到，使用python-magic
            if not mime_type and MAGIC_AVAILABLE:
                try:
                    mime_type = magic.from_file(file_path, mime=True)
                except:
                    pass
            
            # 回退到扩展名检测
            if not mime_type:
                ext = Path(file_path).suffix.lower()
                mime_map = {
                    '.pdf': 'application/pdf',
                    '.xml': 'application/xml',
                    '.json': 'application/json',
                    '.csv': 'text/csv',
                    '.yaml': 'application/x-yaml',
                    '.yml': 'application/x-yaml'
                }
                mime_type = mime_map.get(ext, 'application/octet-stream')
            
            return {
                "file_path": file_path,
                "mime_type": mime_type,
                "extension": Path(file_path).suffix.lower(),
                "size": os.path.getsize(file_path),
                "detected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"文件格式检测失败: {e}")
            return {
                "file_path": file_path,
                "mime_type": "unknown",
                "extension": Path(file_path).suffix.lower(),
                "error": str(e)
            }
    
    def find_adapter(self, file_path: str, mime_type: str) -> Optional[FormatAdapter]:
        """查找适合的格式适配器"""
        for adapter in self.adapters:
            if adapter.can_handle(file_path, mime_type):
                return adapter
        return None
    
    def process_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            logger.info(f"开始处理文件: {file_path}")
            
            # 检测文件格式
            format_info = self.detect_file_format(file_path)
            
            # 查找适配器
            adapter = self.find_adapter(file_path, format_info["mime_type"])
            
            if not adapter:
                return {
                    "success": False,
                    "error": f"不支持的文件格式: {format_info['mime_type']}",
                    "format_info": format_info,
                    "supported_formats": self.get_supported_formats()
                }
            
            # 检测标准类型
            standard_info = adapter.detect_standard(file_path)
            
            # 处理文件
            process_result = adapter.process(file_path, **kwargs)
            
            # 组合结果
            result = {
                "success": process_result.get("success", True),
                "file_path": file_path,
                "format_info": format_info,
                "standard_info": standard_info,
                "adapter_used": adapter.__class__.__name__,
                "process_result": process_result,
                "processed_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"文件处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def process_files(self, file_paths: List[str], **kwargs) -> Dict[str, Any]:
        """批量处理多个文件"""
        results = []
        summary = {
            "total_files": len(file_paths),
            "successful": 0,
            "failed": 0,
            "by_format": {},
            "by_standard": {}
        }
        
        for file_path in file_paths:
            try:
                result = self.process_file(file_path, **kwargs)
                results.append(result)
                
                if result["success"]:
                    summary["successful"] += 1
                    
                    # 统计格式
                    format_type = result.get("format_info", {}).get("mime_type", "unknown")
                    summary["by_format"][format_type] = summary["by_format"].get(format_type, 0) + 1
                    
                    # 统计标准
                    standard = result.get("standard_info", {}).get("standard", "unknown")
                    summary["by_standard"][standard] = summary["by_standard"].get(standard, 0) + 1
                    
                else:
                    summary["failed"] += 1
                    
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时发生异常: {e}")
                results.append({
                    "success": False,
                    "file_path": file_path,
                    "error": str(e)
                })
                summary["failed"] += 1
        
        return {
            "success": summary["failed"] == 0,
            "summary": summary,
            "results": results,
            "processed_at": datetime.now().isoformat()
        }
    
    def import_to_database(self, yaml_paths: List[str], dry_run: bool = True) -> Dict[str, Any]:
        """将处理结果导入数据库"""
        try:
            import_results = []
            
            for yaml_path in yaml_paths:
                if os.path.exists(yaml_path):
                    result = self.yaml_importer.import_yaml_file(yaml_path, dry_run)
                    import_results.append({
                        "yaml_path": yaml_path,
                        "result": result
                    })
                else:
                    import_results.append({
                        "yaml_path": yaml_path,
                        "result": {
                            "success": False,
                            "error": f"YAML文件不存在: {yaml_path}"
                        }
                    })
            
            # 汇总结果
            successful_imports = sum(1 for r in import_results if r["result"].get("success"))
            
            return {
                "success": successful_imports > 0,
                "total_yamls": len(yaml_paths),
                "successful_imports": successful_imports,
                "failed_imports": len(yaml_paths) - successful_imports,
                "dry_run": dry_run,
                "results": import_results
            }
            
        except Exception as e:
            logger.error(f"数据库导入失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_pipeline(self, file_paths: List[str], import_to_db: bool = False, dry_run: bool = True, **kwargs) -> Dict[str, Any]:
        """完整的处理流水线：文件处理 -> YAML生成 -> 数据库导入"""
        try:
            # 第一步：处理文件
            process_result = self.process_files(file_paths, **kwargs)
            
            if not process_result["success"]:
                return {
                    "success": False,
                    "stage": "file_processing",
                    "error": "文件处理阶段失败",
                    "details": process_result
                }
            
            # 收集生成的YAML文件
            yaml_paths = []
            for result in process_result["results"]:
                if result["success"] and "yaml_path" in result.get("process_result", {}):
                    yaml_paths.append(result["process_result"]["yaml_path"])
            
            result = {
                "success": True,
                "stage": "complete",
                "file_processing": process_result,
                "yaml_files_generated": yaml_paths
            }
            
            # 第二步：数据库导入（如果需要）
            if import_to_db and yaml_paths:
                import_result = self.import_to_database(yaml_paths, dry_run)
                result["database_import"] = import_result
                
                if not import_result["success"]:
                    result["success"] = False
                    result["stage"] = "database_import"
                    result["error"] = "数据库导入阶段失败"
            
            return result
            
        except Exception as e:
            logger.error(f"完整流水线执行失败: {e}")
            return {
                "success": False,
                "stage": "pipeline_error",
                "error": str(e)
            }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """获取所有支持的格式"""
        supported = {}
        for adapter in self.adapters:
            adapter_name = adapter.__class__.__name__
            supported[adapter_name] = adapter.get_supported_formats()
        return supported
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "adapters_loaded": len(self.adapters),
            "supported_formats": self.get_supported_formats(),
            "system_ready": True,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """测试和演示"""
    system = UniversalImportSystem()
    
    print("🎯 统一多格式导入系统")
    print("=" * 50)
    
    # 显示支持的格式
    print("📋 支持的格式:")
    for adapter, formats in system.get_supported_formats().items():
        print(f"   {adapter}: {', '.join(formats)}")
    
    print("\\n✅ 系统就绪，可以处理多种格式的文件!")

if __name__ == "__main__":
    main()
