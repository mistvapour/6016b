#!/usr/bin/env python3
from __future__ import annotations

"""
将字段字典候选（normalize_tables输出）转换为 MessageDefinition。
输入结构示例：[{"page": 9, "fields": [{"field":"Range","start":16,"end":31,"units":"m","description":"..."}, ...]}]
策略：
- 取第一页或合并多页字段为一个消息定义（可根据需要扩展分组逻辑）
- dtype 通过字段名与单位启发式猜测：enum/uint/float/string
- 生成最小约束：required=True；若有数值位段则给出最小/最大范围占位（可扩展）
"""

from typing import List, Dict, Any
import re

from backend.schema.message_definition import MessageDefinition, MessageField, FieldConstraint


def _guess_dtype(name: str, units: str | None) -> str:
    n = (name or "").lower()
    if any(k in n for k in ["status", "mode", "type", "enum"]):
        return "enum"
    if units:
        u = units.lower()
        if u in {"m", "km", "nm"}:
            return "uint"
        if u in {"deg", "rad"}:
            return "float"
    if re.search(r"id$|index$|num$", n):
        return "uint"
    return "string"


def _build_field(item: Dict[str, Any]) -> MessageField:
    name = str(item.get("field") or item.get("name") or "field")
    units = item.get("units")
    desc = item.get("description")
    start = item.get("start")
    end = item.get("end")
    bits = None
    if isinstance(start, int) and isinstance(end, int):
        bits = [int(start), int(end)]
    dtype = _guess_dtype(name, units)
    constraint = FieldConstraint(required=True)
    if dtype in ("uint", "float") and bits:
        width = bits[1] - bits[0] + 1
        # 最小占位：无符号整型最大值 2^width-1
        try:
            max_val = float(2 ** width - 1)
            constraint.min_value = 0.0
            constraint.max_value = max_val
        except Exception:
            pass
    return MessageField(name=name, dtype=dtype, units=units, description=desc, bits=bits, children=None, constraint=constraint)


def tables_to_message(pages: List[Dict[str, Any]], label: str = "JX.Y", title: str = "Auto Generated Message") -> MessageDefinition:
    fields: List[MessageField] = []
    for page in pages:
        for item in page.get("fields", []):
            f = _build_field(item)
            fields.append(f)
    return MessageDefinition(label=label, title=title, fields=fields)


def simple_validate_coverage(fields: List[MessageField]) -> Dict[str, Any]:
    covered = []
    for f in fields:
        if f.bits and len(f.bits) == 2:
            covered.append((f.bits[0], f.bits[1]))
    covered.sort()
    total = 0
    merged: List[tuple[int, int]] = []
    for s, e in covered:
        if not merged or s > merged[-1][1] + 1:
            merged.append((s, e))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
    for s, e in merged:
        total += (e - s + 1)
    return {"bit_segments": covered, "merged_segments": merged, "covered_bits": total}


__all__ = ["tables_to_message", "simple_validate_coverage"]


