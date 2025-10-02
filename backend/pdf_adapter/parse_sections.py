"""
PDF章节解析模块
专门针对MIL-STD-6016标准的J系列和Appendix B章节定位
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

@dataclass
class SectionInfo:
    """章节信息"""
    section_type: str  # 'j_message' or 'appendix_b'
    label: str  # 如 'J10.2' 或 'DFI-123'
    title: str
    start_page: int
    end_page: Optional[int] = None
    content: Optional[str] = None
    tables: List[Dict[str, Any]] = None

class SectionParser:
    """6016标准章节解析器"""
    
    def __init__(self):
        # J系列消息模式
        self.j_message_pattern = re.compile(r'^J(\d+(?:\.\d+)?)\s*[:：]?\s*(.+)$', re.MULTILINE)
        
        # Appendix B 模式
        self.dfi_pattern = re.compile(r'^DFI\s*(\d+)\s*[:：]?\s*(.+)$', re.MULTILINE)
        self.dui_pattern = re.compile(r'^DUI\s*(\d+)\s*[:：]?\s*(.+)$', re.MULTILINE)
        self.di_pattern = re.compile(r'^DI\s*[:：]?\s*(.+)$', re.MULTILINE)
        
        # 表格相关关键词
        self.table_keywords = [
            'word', 'bit', 'start', 'end', 'field', 'description',
            'resolution', 'units', 'coding', 'format'
        ]
        
        # 章节标题模式
        self.section_title_pattern = re.compile(r'^Section\s+(\d+)\s*[:：]?\s*(.+)$', re.MULTILINE)
        self.appendix_pattern = re.compile(r'^Appendix\s+([A-Z])\s*[:：]?\s*(.+)$', re.MULTILINE)
    
    def parse_pdf_sections(self, pdf_path: str) -> List[SectionInfo]:
        """解析PDF文档的所有相关章节"""
        sections = []
        
        try:
            doc = fitz.open(pdf_path)
            
            # 1. 解析J系列消息
            j_sections = self._parse_j_messages(doc)
            sections.extend(j_sections)
            
            # 2. 解析Appendix B
            appendix_sections = self._parse_appendix_b(doc)
            sections.extend(appendix_sections)
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Failed to parse PDF sections: {e}")
        
        return sections
    
    def _parse_j_messages(self, doc) -> List[SectionInfo]:
        """解析J系列消息章节"""
        sections = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # 查找J系列消息
            j_matches = self.j_message_pattern.findall(text)
            for j_label, title in j_matches:
                section = SectionInfo(
                    section_type='j_message',
                    label=f"J{j_label}",
                    title=title.strip(),
                    start_page=page_num + 1,
                    content=text
                )
                
                # 查找该消息相关的表格
                section.tables = self._find_tables_in_section(doc, page_num, section)
                sections.append(section)
        
        return sections
    
    def _parse_appendix_b(self, doc) -> List[SectionInfo]:
        """解析Appendix B章节"""
        sections = []
        in_appendix_b = False
        current_dfi = None
        current_dui = None
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # 检查是否进入Appendix B
            if re.search(r'Appendix\s+B\s*[:：]', text, re.IGNORECASE):
                in_appendix_b = True
                continue
            
            if not in_appendix_b:
                continue
            
            # 检查是否离开Appendix B
            if re.search(r'Appendix\s+[C-Z]\s*[:：]', text, re.IGNORECASE):
                break
            
            # 解析DFI
            dfi_matches = self.dfi_pattern.findall(text)
            for dfi_num, dfi_title in dfi_matches:
                current_dfi = {
                    'num': int(dfi_num),
                    'title': dfi_title.strip()
                }
            
            # 解析DUI
            dui_matches = self.dui_pattern.findall(text)
            for dui_num, dui_title in dui_matches:
                current_dui = {
                    'num': int(dui_num),
                    'title': dui_title.strip(),
                    'dfi': current_dfi
                }
            
            # 解析DI
            di_matches = self.di_pattern.findall(text)
            for di_title in di_matches:
                if current_dui:
                    section = SectionInfo(
                        section_type='appendix_b',
                        label=f"DFI-{current_dfi['num']}/DUI-{current_dui['num']}/DI",
                        title=di_title.strip(),
                        start_page=page_num + 1,
                        content=text
                    )
                    sections.append(section)
        
        return sections
    
    def _find_tables_in_section(self, doc, start_page: int, section: SectionInfo) -> List[Dict[str, Any]]:
        """在章节中查找相关表格"""
        tables = []
        
        # 在章节开始页面的后续几页中查找表格
        search_pages = min(start_page + 3, len(doc))  # 最多搜索3页
        
        for page_num in range(start_page - 1, search_pages):
            page = doc[page_num]
            text = page.get_text()
            
            # 查找包含表格关键词的文本
            if self._has_table_indicators(text):
                # 这里可以集成表格提取器
                table_info = {
                    'page': page_num + 1,
                    'indicators': self._extract_table_indicators(text),
                    'content': text
                }
                tables.append(table_info)
        
        return tables
    
    def _has_table_indicators(self, text: str) -> bool:
        """检查文本是否包含表格指示器"""
        text_lower = text.lower()
        
        # 检查是否包含表格关键词
        keyword_count = sum(1 for keyword in self.table_keywords if keyword in text_lower)
        
        # 检查是否包含位段模式
        bit_pattern = re.compile(r'\d+\s*[-–~\.]{1,2}\s*\d+')
        has_bit_ranges = bool(bit_pattern.search(text))
        
        return keyword_count >= 2 and has_bit_ranges
    
    def _extract_table_indicators(self, text: str) -> List[str]:
        """提取表格指示器"""
        indicators = []
        
        for keyword in self.table_keywords:
            if keyword.lower() in text.lower():
                indicators.append(keyword)
        
        # 查找位段范围
        bit_pattern = re.compile(r'\d+\s*[-–~\.]{1,2}\s*\d+')
        bit_ranges = bit_pattern.findall(text)
        if bit_ranges:
            indicators.append(f"bit_ranges: {len(bit_ranges)}")
        
        return indicators
    
    def extract_j_message_fields(self, section: SectionInfo) -> List[Dict[str, Any]]:
        """从J消息章节中提取字段信息"""
        if not section.content:
            return []
        
        fields = []
        lines = section.content.split('\n')
        
        # 查找表格行
        in_table = False
        headers = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是表头
            if self._is_table_header(line):
                in_table = True
                headers = self._parse_table_header(line)
                continue
            
            # 检查是否是数据行
            if in_table and self._is_data_row(line, headers):
                field_data = self._parse_field_row(line, headers)
                if field_data:
                    fields.append(field_data)
        
        return fields
    
    def _is_table_header(self, line: str) -> bool:
        """判断是否是表头行"""
        line_lower = line.lower()
        keyword_count = sum(1 for keyword in self.table_keywords if keyword in line_lower)
        return keyword_count >= 2
    
    def _parse_table_header(self, line: str) -> List[str]:
        """解析表头"""
        # 简单的分割，实际可能需要更复杂的解析
        headers = re.split(r'\s{2,}|\t', line)
        return [h.strip() for h in headers if h.strip()]
    
    def _is_data_row(self, line: str, headers: List[str]) -> bool:
        """判断是否是数据行"""
        # 检查是否包含位段模式
        bit_pattern = re.compile(r'\d+\s*[-–~\.]{1,2}\s*\d+')
        return bool(bit_pattern.search(line))
    
    def _parse_field_row(self, line: str, headers: List[str]) -> Optional[Dict[str, Any]]:
        """解析字段行"""
        try:
            # 简单的分割，实际需要更复杂的解析
            values = re.split(r'\s{2,}|\t', line)
            values = [v.strip() for v in values if v.strip()]
            
            if len(values) < len(headers):
                return None
            
            field_data = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    field_data[header.lower()] = values[i]
            
            # 解析位段
            bit_info = self._parse_bit_range(field_data.get('bit', ''))
            if bit_info:
                field_data['bit_range'] = bit_info
            
            return field_data
            
        except Exception as e:
            logger.error(f"Failed to parse field row: {e}")
            return None
    
    def _parse_bit_range(self, bit_text: str) -> Optional[Dict[str, int]]:
        """解析位段范围"""
        if not bit_text:
            return None
        
        # 匹配各种位段格式
        patterns = [
            r'(?P<start>\d+)\s*[-–~\.]{1,2}\s*(?P<end>\d+)',  # 0-5, 0–5, 0..5
            r'(?P<start>\d+)\s+to\s+(?P<end>\d+)',  # 0 to 5
            r'bits?\s+(?P<start>\d+)\s*[-–~\.]{1,2}\s*(?P<end>\d+)',  # bits 0-5
        ]
        
        for pattern in patterns:
            match = re.search(pattern, bit_text, re.IGNORECASE)
            if match:
                return {
                    'start': int(match.group('start')),
                    'end': int(match.group('end'))
                }
        
        return None

def parse_6016_sections(pdf_path: str) -> Dict[str, List[SectionInfo]]:
    """
    解析6016标准PDF的所有相关章节
    Returns:
        字典，包含'j_messages'和'appendix_b'两个键
    """
    parser = SectionParser()
    sections = parser.parse_pdf_sections(pdf_path)
    
    result = {
        'j_messages': [],
        'appendix_b': []
    }
    
    for section in sections:
        if section.section_type == 'j_message':
            result['j_messages'].append(section)
        elif section.section_type == 'appendix_b':
            result['appendix_b'].append(section)
    
    return result
