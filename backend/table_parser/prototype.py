#!/usr/bin/env python3
"""
表格解析原型（最小实现）：
- 从纯文本中识别类表格段（包含常见列名 keyword）
- 简单列切分与行聚合，占位支持跨页与合并单元格

说明：后续可替换为结构化PDF/Word表格解析器。
"""
from __future__ import annotations

from typing import List, Dict
import re


COMMON_COLS = [
    "word", "bit", "start", "end", "field", "description", "units", "coding",
]


def detect_table_blocks(text: str) -> List[str]:
    blocks: List[str] = []
    lines = text.splitlines()
    window: List[str] = []
    for line in lines:
        window.append(line)
        if len(window) > 30:
            window.pop(0)
        joined = "\n".join(window).lower()
        if sum(1 for c in COMMON_COLS if c in joined) >= 3:
            blocks.append(joined)
            window = []
    return blocks


def parse_block(block: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    head = [c for c in COMMON_COLS if c in block]
    if not head:
        return rows
    for line in block.splitlines():
        cols = re.split(r"\s{2,}|\t|\|", line.strip())
        if len(cols) < 2:
            continue
        row: Dict[str, str] = {}
        for i, key in enumerate(head):
            if i < len(cols):
                row[key] = cols[i]
        if row:
            rows.append(row)
    return rows


def parse_tables_from_text(text: str) -> List[List[Dict[str, str]]]:
    blocks = detect_table_blocks(text)
    return [parse_block(b) for b in blocks]


__all__ = ["parse_tables_from_text"]


