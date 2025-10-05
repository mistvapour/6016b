# backend/mqtt_adapter/normalize_bits.py
import re
import logging

logger = logging.getLogger(__name__)

# MQTT字段编码类型
VBI = "VBI"       # Variable Byte Integer
UTF8 = "UTF8"     # UTF-8 String
UINT = "UINT"     # Unsigned Integer
BIN = "BIN"       # Binary Data
VARB = "VAR-BYTES"  # Variable Length Bytes

# 长度模式匹配
LEN_PAT = re.compile(r'(\d+)\s*byte', re.IGNORECASE)
VBI_PAT = re.compile(r'(vbi|variable\s+byte\s+integer)', re.IGNORECASE)
UTF8_PAT = re.compile(r'(utf-?8|string)', re.IGNORECASE)
VAR_PAT = re.compile(r'var.*byte', re.IGNORECASE)

def parse_field_row(row_data):
    """
    解析表格行数据
    入参: {'name': 字段名, 'len': 长度描述, 'desc': 描述, ...}
    返回: {name, length=None|int, offset_unit='byte', encoding, description}
    """
    if isinstance(row_data, dict):
        name = str(row_data.get('name', '')).strip()
        length_desc = str(row_data.get('len', row_data.get('length', ''))).strip()
        description = str(row_data.get('desc', row_data.get('description', ''))).strip()
    else:
        # 如果是列表或其他格式，尝试解析
        name = str(row_data[0] if len(row_data) > 0 else '').strip()
        length_desc = str(row_data[1] if len(row_data) > 1 else '').strip()
        description = str(row_data[2] if len(row_data) > 2 else '').strip()
    
    # 默认值
    encoding = BIN
    length = None
    offset_unit = "byte"
    
    # 分析长度描述
    length_desc_lower = length_desc.lower()
    
    if VBI_PAT.search(length_desc_lower):
        encoding = VBI
        logger.debug(f"Field {name}: detected VBI encoding")
    elif UTF8_PAT.search(length_desc_lower):
        encoding = UTF8
        logger.debug(f"Field {name}: detected UTF8 encoding")
    elif VAR_PAT.search(length_desc_lower):
        encoding = VARB
        logger.debug(f"Field {name}: detected variable bytes encoding")
    else:
        # 尝试提取固定字节长度
        match = LEN_PAT.search(length_desc_lower)
        if match:
            encoding = UINT
            length = int(match.group(1))
            logger.debug(f"Field {name}: detected {length} byte(s) UINT")
        elif any(digit in length_desc_lower for digit in '0123456789'):
            # 包含数字但不匹配标准模式，尝试提取第一个数字
            numbers = re.findall(r'\d+', length_desc_lower)
            if numbers:
                encoding = UINT
                length = int(numbers[0])
                logger.debug(f"Field {name}: extracted length {length} from '{length_desc}'")
    
    result = {
        "name": name,
        "length": length,
        "offset_unit": offset_unit,
        "encoding": encoding,
        "description": description
    }
    
    logger.debug(f"Parsed field: {result}")
    return result

def normalize_table_data(df, table_type="fields"):
    """
    标准化表格数据为字段列表
    """
    if df.empty or len(df) < 2:
        return []
    
    fields = []
    
    try:
        # 假设第一行是表头
        headers = [str(col).strip().lower() for col in df.iloc[0]]
        
        # 查找关键列索引
        name_col = None
        length_col = None
        desc_col = None
        
        for i, header in enumerate(headers):
            if any(kw in header for kw in ['name', 'field', 'property']):
                name_col = i
            elif any(kw in header for kw in ['length', 'size', 'byte', 'len']):
                length_col = i
            elif any(kw in header for kw in ['description', 'desc', 'comment', 'note']):
                desc_col = i
        
        # 处理数据行
        for i, row in df.iloc[1:].iterrows():
            try:
                row_data = {
                    'name': str(row.iloc[name_col]) if name_col is not None else str(row.iloc[0]),
                    'len': str(row.iloc[length_col]) if length_col is not None else str(row.iloc[1]) if len(row) > 1 else '',
                    'desc': str(row.iloc[desc_col]) if desc_col is not None else str(row.iloc[-1]) if len(row) > 2 else ''
                }
                
                # 跳过空行或无效行
                if not row_data['name'] or row_data['name'].lower() in ['nan', 'none', '']:
                    continue
                
                field = parse_field_row(row_data)
                if field['name']:  # 只添加有名称的字段
                    fields.append(field)
                    
            except Exception as e:
                logger.warning(f"Failed to parse row {i}: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Failed to normalize table data: {e}")
    
    logger.info(f"Normalized {len(fields)} fields from table")
    return fields

def validate_fields(fields):
    """验证字段定义的完整性"""
    issues = []
    
    for i, field in enumerate(fields):
        # 检查必填字段
        if not field.get('name'):
            issues.append(f"Field {i}: Missing name")
        
        # 检查编码与长度的一致性
        encoding = field.get('encoding')
        length = field.get('length')
        
        if encoding == UINT and length is None:
            issues.append(f"Field {field.get('name', i)}: UINT encoding requires fixed length")
        
        if encoding in [VBI, UTF8, VARB] and length is not None:
            issues.append(f"Field {field.get('name', i)}: Variable encoding should not have fixed length")
    
    return issues

def group_fields_by_segment(fields, segment_hints=None):
    """
    根据字段名称和描述将字段分组到不同段
    MQTT通常有：Fixed Header, Variable Header, Properties, Payload
    """
    segments = {
        'Fixed Header': [],
        'Variable Header': [],
        'Properties': [],
        'Payload': []
    }
    
    for field in fields:
        name = field['name'].lower()
        desc = field.get('description', '').lower()
        
        # 分段逻辑
        if any(kw in name for kw in ['control', 'flag', 'type', 'remaining']):
            segments['Fixed Header'].append(field)
        elif any(kw in desc for kw in ['property', 'prop']):
            segments['Properties'].append(field)
        elif any(kw in name for kw in ['payload', 'data', 'message']):
            segments['Payload'].append(field)
        else:
            segments['Variable Header'].append(field)
    
    # 移除空段
    return {k: v for k, v in segments.items() if v}

def calculate_offsets(fields):
    """计算字段偏移量"""
    offset = 0
    
    for field in fields:
        field['offset'] = offset
        
        length = field.get('length')
        if length is not None:
            offset += length
        else:
            # 变长字段，无法计算后续偏移
            field['offset_note'] = "Variable length field"
            break
    
    return fields
