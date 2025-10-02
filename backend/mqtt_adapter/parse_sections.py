# backend/mqtt_adapter/parse_sections.py
import re
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# MQTT控制报文类型正则表达式
CTRL_PKT_RE = re.compile(r'^(CONNECT|CONNACK|PUBLISH|PUBACK|PUBREC|PUBREL|PUBCOMP|SUBSCRIBE|SUBACK|UNSUBSCRIBE|UNSUBACK|PINGREQ|PINGRESP|DISCONNECT|AUTH)\b', re.IGNORECASE | re.MULTILINE)

# 其他重要章节
SECTION_PATTERNS = {
    'properties': re.compile(r'properties|property', re.IGNORECASE),
    'payload': re.compile(r'payload', re.IGNORECASE),
    'variable_header': re.compile(r'variable\s+header', re.IGNORECASE),
    'fixed_header': re.compile(r'fixed\s+header', re.IGNORECASE),
}

def detect_sections(page_texts):
    """
    入参：{page_no: "整页文本"}
    出参：[{"label":"CONNECT","pages":[10,11]}, ...]
    原理：遇到控制报文大标题作为锚点，直到下一个标题前的页
    """
    items = []
    current = None
    
    logger.info(f"Detecting sections in {len(page_texts)} pages")
    
    for pno in sorted(page_texts):
        txt = page_texts[pno]
        
        # 查找控制报文标题
        matches = CTRL_PKT_RE.findall(txt)
        
        if matches:
            # 如果找到新的控制报文，保存之前的
            if current:
                items.append(current)
                logger.debug(f"Section {current['label']}: pages {current['pages']}")
            
            # 开始新的控制报文章节
            packet_type = matches[0].upper()
            current = {
                "label": packet_type,
                "pages": [pno],
                "title": f"{packet_type} Packet",
                "description": f"MQTT {packet_type} control packet specification"
            }
            logger.info(f"Found section: {packet_type} at page {pno}")
            
        elif current:
            # 继续当前章节
            current["pages"].append(pno)
    
    # 保存最后一个章节
    if current:
        items.append(current)
        logger.debug(f"Section {current['label']}: pages {current['pages']}")
    
    logger.info(f"Detected {len(items)} MQTT control packet sections")
    return items

def detect_subsections(page_text):
    """检测页面内的子章节（固定头、可变头、属性、载荷）"""
    subsections = []
    
    for name, pattern in SECTION_PATTERNS.items():
        if pattern.search(page_text):
            subsections.append(name)
    
    return subsections

def extract_page_texts(pdf_path, page_list):
    """从PDF提取页面文本"""
    page_texts = {}
    
    try:
        doc = fitz.open(pdf_path)
        logger.info(f"Opened PDF with {len(doc)} pages")
        
        for p in page_list:
            if 1 <= p <= len(doc):
                try:
                    text = doc[p-1].get_text()
                    page_texts[p] = text
                    logger.debug(f"Page {p}: extracted {len(text)} characters")
                except Exception as e:
                    logger.error(f"Failed to extract text from page {p}: {e}")
            else:
                logger.warning(f"Page {p} is out of range (1-{len(doc)})")
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Failed to open PDF {pdf_path}: {e}")
        raise
    
    logger.info(f"Extracted text from {len(page_texts)} pages")
    return page_texts

def analyze_mqtt_structure(pdf_path, page_range="10-130"):
    """分析MQTT PDF文档结构的便捷函数"""
    # 解析页面范围
    page_list = []
    for part in page_range.split(","):
        if "-" in part:
            a, b = part.split("-")
            page_list += list(range(int(a), int(b) + 1))
        else:
            page_list.append(int(part))
    
    # 提取页面文本
    page_texts = extract_page_texts(pdf_path, page_list)
    
    # 检测章节
    sections = detect_sections(page_texts)
    
    # 为每个章节添加子章节信息
    for section in sections:
        section['subsections'] = []
        for page in section['pages']:
            if page in page_texts:
                subsections = detect_subsections(page_texts[page])
                section['subsections'].extend(subsections)
        
        # 去重
        section['subsections'] = list(set(section['subsections']))
    
    return sections, page_texts
