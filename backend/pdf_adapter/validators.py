"""
校验与质检模块
实现位段、词典树、单位、版本差异等校验
"""
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
import re
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ValidationError:
    """校验错误"""
    error_type: str
    message: str
    field_path: str
    severity: str  # 'error', 'warning', 'info'
    suggested_fix: Optional[str] = None

@dataclass
class ValidationResult:
    """校验结果"""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    coverage: float
    confidence: float

class BitRangeValidator:
    """位段校验器"""
    
    def __init__(self, max_bits: int = 70):
        self.max_bits = max_bits
    
    def validate_bit_ranges(self, fields: List[Dict[str, Any]]) -> List[ValidationError]:
        """校验位段范围"""
        errors = []
        
        # 1. 检查位段边界
        for i, field in enumerate(fields):
            if 'bit_range' in field:
                bit_range = field['bit_range']
                start = bit_range.get('start', 0)
                end = bit_range.get('end', 0)
                
                if start < 0 or start >= self.max_bits:
                    errors.append(ValidationError(
                        error_type='bit_range_boundary',
                        message=f"Start bit {start} is out of bounds (0-{self.max_bits-1})",
                        field_path=f"fields[{i}].bit_range.start",
                        severity='error',
                        suggested_fix=f"Adjust start bit to be between 0 and {self.max_bits-1}"
                    ))
                
                if end < 0 or end >= self.max_bits:
                    errors.append(ValidationError(
                        error_type='bit_range_boundary',
                        message=f"End bit {end} is out of bounds (0-{self.max_bits-1})",
                        field_path=f"fields[{i}].bit_range.end",
                        severity='error',
                        suggested_fix=f"Adjust end bit to be between 0 and {self.max_bits-1}"
                    ))
                
                if start > end:
                    errors.append(ValidationError(
                        error_type='bit_range_order',
                        message=f"Start bit {start} is greater than end bit {end}",
                        field_path=f"fields[{i}].bit_range",
                        severity='error',
                        suggested_fix="Swap start and end bits"
                    ))
        
        # 2. 检查位段重叠
        bit_ranges = []
        for i, field in enumerate(fields):
            if 'bit_range' in field:
                bit_range = field['bit_range']
                bit_ranges.append((i, bit_range))
        
        for i in range(len(bit_ranges)):
            for j in range(i + 1, len(bit_ranges)):
                idx1, range1 = bit_ranges[i]
                idx2, range2 = bit_ranges[j]
                
                if self._ranges_overlap(range1, range2):
                    errors.append(ValidationError(
                        error_type='bit_range_overlap',
                        message=f"Bit ranges overlap: {range1['start']}-{range1['end']} and {range2['start']}-{range2['end']}",
                        field_path=f"fields[{idx1}].bit_range",
                        severity='error',
                        suggested_fix="Adjust bit ranges to avoid overlap"
                    ))
        
        # 3. 检查位段覆盖率
        total_covered = self._calculate_coverage(bit_ranges)
        if total_covered < self.max_bits:
            missing_bits = self.max_bits - total_covered
            errors.append(ValidationError(
                error_type='bit_coverage',
                message=f"Only {total_covered}/{self.max_bits} bits are covered, {missing_bits} bits are missing",
                field_path="fields",
                severity='warning',
                suggested_fix="Add fields to cover missing bits or mark as reserved"
            ))
        
        return errors
    
    def _ranges_overlap(self, range1: Dict[str, int], range2: Dict[str, int]) -> bool:
        """检查两个位段是否重叠"""
        return (range1['start'] <= range2['end'] and range2['start'] <= range1['end'])
    
    def _calculate_coverage(self, bit_ranges: List[Tuple[int, Dict[str, int]]]) -> int:
        """计算位段覆盖率"""
        covered_bits = set()
        for _, bit_range in bit_ranges:
            for bit in range(bit_range['start'], bit_range['end'] + 1):
                covered_bits.add(bit)
        return len(covered_bits)

class DictionaryTreeValidator:
    """词典树校验器"""
    
    def validate_dfiduidi(self, dfiduidi_list: List[Dict[str, Any]]) -> List[ValidationError]:
        """校验DFI/DUI/DI层级关系"""
        errors = []
        
        # 构建DFI和DUI的映射
        dfi_map = {}
        dui_map = {}
        
        for dfiduidi in dfiduidi_list:
            dfi = dfiduidi.get('dfi', {})
            dfi_num = dfi.get('num')
            if dfi_num is not None:
                dfi_map[dfi_num] = dfi
            
            for dui in dfiduidi.get('dui', []):
                dui_num = dui.get('num')
                dfi_num = dui.get('dfi_num')
                if dui_num is not None and dfi_num is not None:
                    dui_map[dui_num] = {'dfi_num': dfi_num, 'dui': dui}
        
        # 校验DUI的DFI引用
        for dui_num, dui_info in dui_map.items():
            dfi_num = dui_info['dfi_num']
            if dfi_num not in dfi_map:
                errors.append(ValidationError(
                    error_type='dui_dfi_reference',
                    message=f"DUI {dui_num} references non-existent DFI {dfi_num}",
                    field_path=f"dui[{dui_num}].dfi_num",
                    severity='error',
                    suggested_fix=f"Create DFI {dfi_num} or correct the reference"
                ))
        
        # 校验DI的DUI引用
        for dfiduidi in dfiduidi_list:
            for di in dfiduidi.get('di', []):
                dui_num = di.get('dui_num')
                if dui_num is not None and dui_num not in dui_map:
                    errors.append(ValidationError(
                        error_type='di_dui_reference',
                        message=f"DI {di.get('code', '')} references non-existent DUI {dui_num}",
                        field_path=f"di[{di.get('code', '')}].dui_num",
                        severity='error',
                        suggested_fix=f"Create DUI {dui_num} or correct the reference"
                    ))
        
        return errors

class UnitValidator:
    """单位校验器"""
    
    def __init__(self):
        # 标准单位转换表
        self.unit_conversions = {
            'deg': {'base_si': 'rad', 'factor': 0.0174532925, 'offset': 0.0},
            'rad': {'base_si': 'rad', 'factor': 1.0, 'offset': 0.0},
            'ft': {'base_si': 'm', 'factor': 0.3048, 'offset': 0.0},
            'm': {'base_si': 'm', 'factor': 1.0, 'offset': 0.0},
            'kts': {'base_si': 'm/s', 'factor': 0.514444, 'offset': 0.0},
            'm/s': {'base_si': 'm/s', 'factor': 1.0, 'offset': 0.0},
            'ft/s': {'base_si': 'm/s', 'factor': 0.3048, 'offset': 0.0},
        }
    
    def validate_units(self, fields: List[Dict[str, Any]]) -> List[ValidationError]:
        """校验单位定义和转换"""
        errors = []
        
        for i, field in enumerate(fields):
            units = field.get('units', [])
            if not units:
                continue
            
            for unit in units:
                if unit not in self.unit_conversions:
                    errors.append(ValidationError(
                        error_type='unknown_unit',
                        message=f"Unknown unit: {unit}",
                        field_path=f"fields[{i}].units",
                        severity='warning',
                        suggested_fix=f"Add unit definition for {unit} or use a standard unit"
                    ))
        
        return errors
    
    def validate_unit_consistency(self, fields: List[Dict[str, Any]]) -> List[ValidationError]:
        """校验单位一致性"""
        errors = []
        
        # 按字段名分组，检查相同字段名的单位是否一致
        field_units = {}
        for i, field in enumerate(fields):
            field_name = field.get('field_name', '')
            units = field.get('units', [])
            if field_name and units:
                if field_name not in field_units:
                    field_units[field_name] = []
                field_units[field_name].append((i, units))
        
        for field_name, unit_lists in field_units.items():
            if len(unit_lists) > 1:
                # 检查所有单位列表是否一致
                first_units = set(unit_lists[0][1])
                for i, units in unit_lists[1:]:
                    current_units = set(units)
                    if first_units != current_units:
                        errors.append(ValidationError(
                            error_type='unit_inconsistency',
                            message=f"Field '{field_name}' has inconsistent units: {first_units} vs {current_units}",
                            field_path=f"fields[{i}].units",
                            severity='warning',
                            suggested_fix="Standardize units for the same field name"
                        ))
        
        return errors

class VersionValidator:
    """版本校验器"""
    
    def validate_version_consistency(self, sim_data: Dict[str, Any]) -> List[ValidationError]:
        """校验版本一致性"""
        errors = []
        
        # 检查版本号格式
        version = sim_data.get('edition', '')
        if not re.match(r'^[A-Z]$', version):
            errors.append(ValidationError(
                error_type='version_format',
                message=f"Invalid version format: {version}",
                field_path="edition",
                severity='error',
                suggested_fix="Use single uppercase letter (e.g., 'A', 'B', 'C')"
            ))
        
        return errors
    
    def detect_version_changes(self, old_sim: Dict[str, Any], new_sim: Dict[str, Any]) -> List[ValidationError]:
        """检测版本间的变化"""
        errors = []
        
        old_version = old_sim.get('edition', '')
        new_version = new_sim.get('edition', '')
        
        if old_version == new_version:
            return errors
        
        # 比较J消息
        old_messages = {msg['label']: msg for msg in old_sim.get('j_messages', [])}
        new_messages = {msg['label']: msg for msg in new_sim.get('j_messages', [])}
        
        # 检查新增的消息
        for label in new_messages:
            if label not in old_messages:
                errors.append(ValidationError(
                    error_type='version_change',
                    message=f"New message added: {label}",
                    field_path=f"j_messages[{label}]",
                    severity='info',
                    suggested_fix=f"Document the addition of {label} in version {new_version}"
                ))
        
        # 检查删除的消息
        for label in old_messages:
            if label not in new_messages:
                errors.append(ValidationError(
                    error_type='version_change',
                    message=f"Message removed: {label}",
                    field_path=f"j_messages[{label}]",
                    severity='warning',
                    suggested_fix=f"Document the removal of {label} in version {new_version}"
                ))
        
        return errors

class ConfidenceValidator:
    """置信度校验器"""
    
    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
    
    def validate_confidence(self, extraction_results: List[Dict[str, Any]]) -> List[ValidationError]:
        """校验提取结果的置信度"""
        errors = []
        
        for i, result in enumerate(extraction_results):
            confidence = result.get('confidence', 0.0)
            if confidence < self.min_confidence:
                errors.append(ValidationError(
                    error_type='low_confidence',
                    message=f"Low confidence extraction: {confidence:.2f} < {self.min_confidence}",
                    field_path=f"extraction_results[{i}].confidence",
                    severity='warning',
                    suggested_fix="Review and manually verify the extraction result"
                ))
        
        return errors

class ComprehensiveValidator:
    """综合校验器"""
    
    def __init__(self, max_bits: int = 70, min_confidence: float = 0.7):
        self.bit_validator = BitRangeValidator(max_bits)
        self.dict_validator = DictionaryTreeValidator()
        self.unit_validator = UnitValidator()
        self.version_validator = VersionValidator()
        self.confidence_validator = ConfidenceValidator(min_confidence)
    
    def validate_sim(self, sim: Dict[str, Any]) -> ValidationResult:
        """综合校验SIM"""
        errors = []
        warnings = []
        
        # 1. 校验位段
        j_messages = sim.get('j_messages', [])
        for message in j_messages:
            for word in message.get('words', []):
                fields = word.get('fields', [])
                bit_errors = self.bit_validator.validate_bit_ranges(fields)
                errors.extend([e for e in bit_errors if e.severity == 'error'])
                warnings.extend([e for e in bit_errors if e.severity == 'warning'])
        
        # 2. 校验词典树
        dfiduidi_errors = self.dict_validator.validate_dfiduidi(sim.get('dfi_dui_di', []))
        errors.extend([e for e in dfiduidi_errors if e.severity == 'error'])
        warnings.extend([e for e in dfiduidi_errors if e.severity == 'warning'])
        
        # 3. 校验单位
        for message in j_messages:
            for word in message.get('words', []):
                fields = word.get('fields', [])
                unit_errors = self.unit_validator.validate_units(fields)
                warnings.extend([e for e in unit_errors if e.severity == 'warning'])
                
                consistency_errors = self.unit_validator.validate_unit_consistency(fields)
                warnings.extend([e for e in consistency_errors if e.severity == 'warning'])
        
        # 4. 校验版本
        version_errors = self.version_validator.validate_version_consistency(sim)
        errors.extend([e for e in version_errors if e.severity == 'error'])
        warnings.extend([e for e in version_errors if e.severity == 'warning'])
        
        # 5. 计算覆盖率
        total_coverage = self._calculate_total_coverage(sim)
        
        # 6. 计算整体置信度
        overall_confidence = self._calculate_overall_confidence(sim)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            coverage=total_coverage,
            confidence=overall_confidence
        )
    
    def _calculate_total_coverage(self, sim: Dict[str, Any]) -> float:
        """计算总体覆盖率"""
        total_bits = 0
        max_bits = 70
        
        for message in sim.get('j_messages', []):
            for word in message.get('words', []):
                for field in word.get('fields', []):
                    if 'bits' in field and isinstance(field['bits'], list) and len(field['bits']) == 2:
                        start, end = field['bits']
                        total_bits += (end - start + 1)
        
        return total_bits / max_bits if max_bits > 0 else 0.0
    
    def _calculate_overall_confidence(self, sim: Dict[str, Any]) -> float:
        """计算整体置信度"""
        confidences = []
        
        # 从元数据中获取置信度
        metadata = sim.get('metadata', {})
        if 'confidence' in metadata:
            confidences.append(metadata['confidence'])
        
        # 从字段中获取置信度
        for message in sim.get('j_messages', []):
            for word in message.get('words', []):
                for field in word.get('fields', []):
                    if 'confidence' in field:
                        confidences.append(field['confidence'])
        
        if not confidences:
            return 0.5  # 默认置信度
        
        return sum(confidences) / len(confidences)

def validate_pdf_extraction(extraction_data: Dict[str, Any]) -> ValidationResult:
    """校验PDF提取数据"""
    validator = ComprehensiveValidator()
    return validator.validate_sim(extraction_data)

def generate_validation_report(result: ValidationResult) -> str:
    """生成校验报告"""
    report = []
    report.append("=== PDF Extraction Validation Report ===")
    report.append(f"Valid: {result.valid}")
    report.append(f"Coverage: {result.coverage:.2%}")
    report.append(f"Confidence: {result.confidence:.2%}")
    report.append("")
    
    if result.errors:
        report.append("ERRORS:")
        for error in result.errors:
            report.append(f"  [{error.severity.upper()}] {error.field_path}: {error.message}")
            if error.suggested_fix:
                report.append(f"    Suggested fix: {error.suggested_fix}")
        report.append("")
    
    if result.warnings:
        report.append("WARNINGS:")
        for warning in result.warnings:
            report.append(f"  [{warning.severity.upper()}] {warning.field_path}: {warning.message}")
            if warning.suggested_fix:
                report.append(f"    Suggested fix: {warning.suggested_fix}")
        report.append("")
    
    return "\n".join(report)
