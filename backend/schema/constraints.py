#!/usr/bin/env python3
"""
扩展约束表达式：
- depends_on: 依赖字段
- when: 条件表达式（例如 "field_A > 0"）
- units/enum 引用标准字典
- 校验器实现
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ExtendedConstraint:
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum: Optional[List[str]] = None
    pattern: Optional[str] = None
    # 扩展：
    depends_on: Optional[List[str]] = None
    when: Optional[str] = None  # 条件表达式
    units_ref: Optional[str] = None  # 如 "deg@6016B"
    enum_ref: Optional[str] = None  # 如 "weapon_status@6016B"


@dataclass
class UnitsDict:
    symbol: str
    base_si: Optional[str] = None
    factor: Optional[float] = None
    offset: Optional[float] = None
    description: Optional[str] = None

    @staticmethod
    def parse_ref(ref: str) -> tuple[str, str]:
        # "deg@6016B" -> ("deg", "6016B")
        if "@" not in ref:
            return ref, "default"
        parts = ref.rsplit("@", 1)
        return parts[0], parts[1]


@dataclass
class EnumDict:
    key: str
    items: List[Dict[str, str]]

    @staticmethod
    def parse_ref(ref: str) -> tuple[str, str]:
        # "weapon_status@6016B" -> ("weapon_status", "6016B")
        if "@" not in ref:
            return ref, "default"
        parts = ref.rsplit("@", 1)
        return parts[0], parts[1]


class ConstraintValidator:
    def __init__(self, units_dicts: Optional[Dict[str, UnitsDict]] = None, enum_dicts: Optional[Dict[str, EnumDict]] = None):
        self.units_dicts = units_dicts or {}
        self.enum_dicts = enum_dicts or {}

    def validate_field(self, field_value: Any, constraint: ExtendedConstraint, context: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """返回 (是否有效, 错误信息)"""
        context = context or {}
        # 必填校验
        if constraint.required and (field_value is None or field_value == ""):
            return False, "Required field is missing"
        if field_value is None:
            return True, None
        # 依赖校验
        if constraint.depends_on:
            for dep in constraint.depends_on:
                if dep not in context or context[dep] is None:
                    return False, f"Dependency field '{dep}' is missing"
        # when 条件（简易：仅支持简单比较）
        if constraint.when:
            if not self._evaluate_when(constraint.when, context):
                return False, f"When condition not met: {constraint.when}"
        # 范围
        if isinstance(field_value, (int, float)):
            if constraint.min_value is not None and field_value < constraint.min_value:
                return False, f"Value {field_value} < min={constraint.min_value}"
            if constraint.max_value is not None and field_value > constraint.max_value:
                return False, f"Value {field_value} > max={constraint.max_value}"
        # enum 引用
        if constraint.enum_ref and constraint.enum:
            symbol, version = EnumDict.parse_ref(constraint.enum_ref)
            valid = str(field_value) in constraint.enum
            if not valid:
                return False, f"Enum value not in {constraint.enum}"
        # pattern
        if constraint.pattern:
            import re
            if not re.match(constraint.pattern, str(field_value)):
                return False, f"Pattern mismatch: {constraint.pattern}"
        return True, None

    def _evaluate_when(self, expr: str, context: Dict[str, Any]) -> bool:
        # 极简实现：支持 "field > 0" 这样的表达式
        try:
            for k, v in context.items():
                expr = expr.replace(k, str(v))
            return eval(expr)
        except Exception:
            return False


__all__ = ["ExtendedConstraint", "UnitsDict", "EnumDict", "ConstraintValidator"]

