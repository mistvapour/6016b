"""
位段和单位标准化模块
处理各种位段格式和单位转换
"""
import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BitRange:
    """位段范围"""
    start: int
    end: int
    length: int
    
    def __post_init__(self):
        self.length = self.end - self.start + 1
    
    def overlaps(self, other: 'BitRange') -> bool:
        """检查是否与另一个位段重叠"""
        return not (self.end < other.start or other.end < self.start)
    
    def is_valid(self, max_bits: int = 70) -> bool:
        """检查位段是否有效"""
        return 0 <= self.start <= self.end < max_bits

@dataclass
class UnitInfo:
    """单位信息"""
    symbol: str
    base_si: str
    factor: float
    offset: float = 0.0
    description: str = ""

class BitRangeNormalizer:
    """位段范围标准化器"""
    
    def __init__(self):
        # 位段范围模式
        self.bit_patterns = [
            # 标准格式: 0-5, 0–5, 0..5
            re.compile(r'(?P<start>\d+)\s*[-–~\.]{1,2}\s*(?P<end>\d+)'),
            # 英文格式: 0 to 5
            re.compile(r'(?P<start>\d+)\s+to\s+(?P<end>\d+)', re.IGNORECASE),
            # bits格式: bits 0-5
            re.compile(r'bits?\s+(?P<start>\d+)\s*[-–~\.]{1,2}\s*(?P<end>\d+)', re.IGNORECASE),
            # 单个位: bit 5
            re.compile(r'bit\s+(?P<start>\d+)', re.IGNORECASE),
        ]
        
        # 单位模式
        self.unit_patterns = {
            'deg': re.compile(r'\b(deg|°|degree|degrees)\b', re.IGNORECASE),
            'rad': re.compile(r'\b(rad|radian|radians)\b', re.IGNORECASE),
            'ft': re.compile(r'\b(ft|feet|foot)\b', re.IGNORECASE),
            'm': re.compile(r'\b(m|meter|meters|metre|metres)\b', re.IGNORECASE),
            'kts': re.compile(r'\b(kts|knots?)\b', re.IGNORECASE),
            'm/s': re.compile(r'\b(m/s|meters?/second|metres?/second)\b', re.IGNORECASE),
            'ft/s': re.compile(r'\b(ft/s|feet?/second)\b', re.IGNORECASE),
        }
        
        # 单位转换表
        self.unit_conversions = {
            'deg': UnitInfo('deg', 'rad', 0.0174532925, 0.0, 'degrees'),
            'rad': UnitInfo('rad', 'rad', 1.0, 0.0, 'radians'),
            'ft': UnitInfo('ft', 'm', 0.3048, 0.0, 'feet'),
            'm': UnitInfo('m', 'm', 1.0, 0.0, 'meters'),
            'kts': UnitInfo('kts', 'm/s', 0.514444, 0.0, 'knots'),
            'm/s': UnitInfo('m/s', 'm/s', 1.0, 0.0, 'meters per second'),
            'ft/s': UnitInfo('ft/s', 'm/s', 0.3048, 0.0, 'feet per second'),
        }
    
    def normalize_bit_range(self, bit_text: str) -> Optional[BitRange]:
        """标准化位段范围"""
        if not bit_text or not bit_text.strip():
            return None
        
        bit_text = bit_text.strip()
        
        # 尝试各种模式
        for pattern in self.bit_patterns:
            match = pattern.search(bit_text)
            if match:
                start = int(match.group('start'))
                end = int(match.group('end')) if 'end' in match.groupdict() else start
                
                # 确保start <= end
                if start > end:
                    start, end = end, start
                
                return BitRange(start=start, end=end)
        
        # 如果都不匹配，尝试直接解析数字
        numbers = re.findall(r'\d+', bit_text)
        if len(numbers) >= 2:
            start, end = int(numbers[0]), int(numbers[1])
            if start > end:
                start, end = end, start
            return BitRange(start=start, end=end)
        elif len(numbers) == 1:
            start = end = int(numbers[0])
            return BitRange(start=start, end=end)
        
        logger.warning(f"Could not parse bit range: {bit_text}")
        return None
    
    def extract_units(self, text: str) -> List[str]:
        """从文本中提取单位"""
        units = []
        for unit_type, pattern in self.unit_patterns.items():
            if pattern.search(text):
                units.append(unit_type)
        return units
    
    def normalize_units(self, units: List[str]) -> List[UnitInfo]:
        """标准化单位"""
        normalized = []
        for unit in units:
            if unit in self.unit_conversions:
                normalized.append(self.unit_conversions[unit])
        return normalized
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """转换单位"""
        if from_unit not in self.unit_conversions or to_unit not in self.unit_conversions:
            return None
        
        from_info = self.unit_conversions[from_unit]
        to_info = self.unit_conversions[to_unit]
        
        # 先转换为SI基准单位
        si_value = value * from_info.factor + from_info.offset
        
        # 再转换为目标单位
        if to_info.factor != 0:
            result = (si_value - to_info.offset) / to_info.factor
            return result
        
        return None

class FieldNormalizer:
    """字段标准化器"""
    
    def __init__(self):
        self.bit_normalizer = BitRangeNormalizer()
        
        # 全角半角转换
        self.full_to_half = str.maketrans(
            '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ',
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        )
        
        # 连字替换
        self.ligature_replacements = {
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            '—': '-',
            '–': '-',
            '…': '...',
        }
    
    def normalize_field_name(self, name: str) -> str:
        """标准化字段名"""
        if not name:
            return ""
        
        # 全角转半角
        name = name.translate(self.full_to_half)
        
        # 替换连字
        for old, new in self.ligature_replacements.items():
            name = name.replace(old, new)
        
        # 去除多余空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def normalize_field_data(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化字段数据"""
        normalized = {}
        
        # 标准化字段名
        if 'field' in field_data:
            normalized['field_name'] = self.normalize_field_name(field_data['field'])
        
        # 标准化位段
        bit_fields = ['bit', 'start', 'end', 'bits']
        bit_text = None
        for field in bit_fields:
            if field in field_data and field_data[field]:
                bit_text = field_data[field]
                break
        
        if bit_text:
            bit_range = self.bit_normalizer.normalize_bit_range(bit_text)
            if bit_range:
                normalized['bit_range'] = {
                    'start': bit_range.start,
                    'end': bit_range.end,
                    'length': bit_range.length
                }
        
        # 标准化描述
        if 'description' in field_data:
            normalized['description'] = self.normalize_field_name(field_data['description'])
        
        # 提取单位
        description = normalized.get('description', '')
        if description:
            units = self.bit_normalizer.extract_units(description)
            if units:
                normalized['units'] = units
        
        # 保留其他字段
        for key, value in field_data.items():
            if key not in ['field', 'bit', 'start', 'end', 'bits', 'description']:
                normalized[key] = value
        
        return normalized
    
    def validate_bit_ranges(self, fields: List[Dict[str, Any]], max_bits: int = 70) -> List[Dict[str, Any]]:
        """验证位段范围"""
        errors = []
        
        # 检查每个字段的位段
        for i, field in enumerate(fields):
            if 'bit_range' in field:
                bit_range = field['bit_range']
                if not (0 <= bit_range['start'] <= bit_range['end'] < max_bits):
                    errors.append({
                        'field_index': i,
                        'field_name': field.get('field_name', ''),
                        'error': f"Bit range {bit_range['start']}-{bit_range['end']} is out of bounds (0-{max_bits-1})"
                    })
        
        # 检查重叠
        bit_ranges = []
        for i, field in enumerate(fields):
            if 'bit_range' in field:
                bit_range = field['bit_range']
                bit_ranges.append((i, bit_range))
        
        for i in range(len(bit_ranges)):
            for j in range(i + 1, len(bit_ranges)):
                idx1, range1 = bit_ranges[i]
                idx2, range2 = bit_ranges[j]
                
                if (range1['start'] <= range2['end'] and range2['start'] <= range1['end']):
                    errors.append({
                        'field_index': idx1,
                        'field_name': fields[idx1].get('field_name', ''),
                        'error': f"Bit range overlaps with field at index {idx2}"
                    })
        
        return errors

def normalize_pdf_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """标准化PDF提取的原始数据"""
    normalizer = FieldNormalizer()
    normalized_data = []
    
    for field_data in raw_data:
        normalized = normalizer.normalize_field_data(field_data)
        if normalized:
            normalized_data.append(normalized)
    
    return normalized_data

def validate_extracted_data(fields: List[Dict[str, Any]], max_bits: int = 70) -> Dict[str, Any]:
    """验证提取的数据"""
    normalizer = FieldNormalizer()
    
    # 验证位段
    bit_errors = normalizer.validate_bit_ranges(fields, max_bits)
    
    # 计算覆盖率
    total_bits = 0
    for field in fields:
        if 'bit_range' in field:
            total_bits += field['bit_range']['length']
    
    coverage = total_bits / max_bits if max_bits > 0 else 0
    
    return {
        'valid': len(bit_errors) == 0,
        'bit_errors': bit_errors,
        'coverage': coverage,
        'total_bits_used': total_bits,
        'max_bits': max_bits,
        'missing_bits': max_bits - total_bits
    }
