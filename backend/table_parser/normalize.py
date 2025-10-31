#!/usr/bin/env python3
"""
将启发式表格候选归一化为字段字典候选：
- 识别表头并映射标准列: field/start/end/bit/units/description
- 解析位段（如"0-5"或"0 – 5"等），提取start/end
- 生成结构化字段条目，过滤空行，导出为列表
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
import re


HEADER_ALIASES = {
    "field": {"field", "字段", "name", "项", "参数"},
    "start": {"start", "起始", "begin", "from"},
    "end": {"end", "结束", "to"},
    "bit": {"bit", "bits", "位", "位段"},
    "units": {"units", "单位"},
    "description": {"description", "desc", "说明", "描述"},
}


def _canon(s: str) -> str:
    return (s or "").strip().lower()


def _guess_header_map(header_row: List[str]) -> Dict[int, str]:
    mapping: Dict[int, str] = {}
    for idx, raw in enumerate(header_row):
        h = _canon(raw)
        for key, aliases in HEADER_ALIASES.items():
            if any(a in h for a in aliases):
                mapping[idx] = key
                break
    # 兜底：若检测到 bit 列但无 start/end，则后续按 bit 解析位段
    return mapping


def _parse_bits(text: str) -> Optional[Tuple[int, int]]:
    if not text:
        return None
    t = text.strip()
    m = re.search(r"(\d+)\s*[-–~\.]{1,2}\s*(\d+)", t)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b:
            return a, b
        return b, a
    # 单值位（如"5"）
    if re.fullmatch(r"\d+", t):
        v = int(t)
        return v, v
    return None


def normalize_table_rows(rows: List[List[str]]) -> List[Dict[str, Any]]:
    if not rows:
        return []
    # 选第一行作表头
    header = rows[0]
    body = rows[1:]
    hmap = _guess_header_map(header)
    out: List[Dict[str, Any]] = []
    for r in body:
        if not any((c or '').strip() for c in r):
            continue
        item: Dict[str, Any] = {}
        # 先按映射填充
        for idx, val in enumerate(r):
            key = hmap.get(idx)
            if not key:
                continue
            v = (val or "").strip()
            if not v:
                continue
            item[key] = v
        # 若存在 bit 列，则解析位段
        if "bit" in item and ("start" not in item or "end" not in item):
            bits = _parse_bits(item.get("bit", ""))
            if bits:
                item["start"], item["end"] = bits[0], bits[1]
        # 清洗：确保 field 存在，或至少有 start/end
        if not item and len(r) >= 1:
            # 尝试将第1列作为字段名
            if r[0].strip():
                item["field"] = r[0].strip()
        if not item:
            continue
        out.append(item)
    return out


def normalize_tables(pages_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    输入：parse_tables_from_pdf 的结果列表
    输出：[{page:int, fields:[{field,start,end,units,description,...}, ...]}]
    """
    results: List[Dict[str, Any]] = []
    for t in pages_tables:
        rows = t.get("rows") or []
        norm = normalize_table_rows(rows)
        if norm:
            results.append({"page": t.get("page"), "fields": norm})
    return results


__all__ = ["normalize_tables", "normalize_table_rows"]


