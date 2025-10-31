#!/usr/bin/env python3
"""
基于 PyMuPDF 的表格解析原型（启发式）：
- 逐页读取文字块（spans）及其 bbox
- 以 y 轴聚类形成行，以 x 轴投影形成列
- 合并相邻跨度，输出简化的二维表结构

注意：
- 仅为最小可用原型，适合规则文本型表格；对图片型/复杂跨页表格需后续OCR/版面增强。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import fitz  # PyMuPDF


@dataclass
class Cell:
    text: str
    x0: float
    x1: float


def _extract_spans(page) -> List[Tuple[str, Tuple[float, float, float, float]]]:
    spans: List[Tuple[str, Tuple[float, float, float, float]]] = []
    blocks = page.get_text("dict").get("blocks", [])
    for b in blocks:
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                text = (s.get("text") or "").strip()
                if not text:
                    continue
                bbox = tuple(s.get("bbox") or (0, 0, 0, 0))
                spans.append((text, bbox))
    return spans


def _cluster_rows(spans: List[Tuple[str, Tuple[float, float, float, float]]], y_tol: float = 2.5) -> List[List[Cell]]:
    # 根据 y0 聚类为行
    spans_sorted = sorted(spans, key=lambda it: (round(it[1][1], 1), it[1][0]))
    rows: List[List[Cell]] = []
    current: List[Cell] = []
    current_y: float | None = None
    for text, (x0, y0, x1, y1) in spans_sorted:
        if current_y is None:
            current_y = y0
            current = [Cell(text=text, x0=x0, x1=x1)]
            continue
        if abs(y0 - current_y) <= y_tol:
            current.append(Cell(text=text, x0=x0, x1=x1))
        else:
            rows.append(sorted(current, key=lambda c: c.x0))
            current = [Cell(text=text, x0=x0, x1=x1)]
            current_y = y0
    if current:
        rows.append(sorted(current, key=lambda c: c.x0))
    return rows


def _project_columns(rows: List[List[Cell]], min_col_gap: float = 12.0) -> List[float]:
    # 根据x0分布估计列起点
    x_positions: List[float] = []
    for r in rows:
        for c in r:
            x_positions.append(c.x0)
    x_positions = sorted(x_positions)
    # 合并相近的x为同一列
    columns: List[float] = []
    for x in x_positions:
        if not columns or abs(x - columns[-1]) > min_col_gap:
            columns.append(x)
    return columns


def _row_to_cells(r: List[Cell], columns: List[float]) -> List[str]:
    # 将行单元格对齐到列
    out = [""] * len(columns)
    j = 0
    for c in r:
        while j + 1 < len(columns) and c.x0 - columns[j + 1] > 0:
            j += 1
        # 合并多span文本
        if out[j]:
            out[j] += " " + c.text
        else:
            out[j] = c.text
    return [x.strip() for x in out]


def parse_tables_from_pdf(pdf_path: str, pages: str | None = None) -> List[Dict[str, Any]]:
    """
    返回每页的表格猜测：[{page:int, columns:[float], rows:[[str,...]]}, ...]
    """
    doc = fitz.open(pdf_path)
    page_list = list(range(len(doc)))
    if pages:
        # 形如 "1-3,5" → 转为0基索引
        tmp: List[int] = []
        for part in pages.split(','):
            part = part.strip()
            if '-' in part:
                a, b = part.split('-')
                tmp.extend(list(range(int(a)-1, int(b))))
            else:
                tmp.append(int(part)-1)
        page_list = [p for p in tmp if 0 <= p < len(doc)]

    results: List[Dict[str, Any]] = []
    for p in page_list:
        page = doc[p]
        spans = _extract_spans(page)
        if not spans:
            continue
        rows = _cluster_rows(spans)
        if not rows:
            continue
        columns = _project_columns(rows)
        # 过滤过短行
        grid = [cells for r in rows if len((cells := _row_to_cells(r, columns))) >= 2]
        # 简单启发：若包含典型列头关键词，认为该页可能存在表格
        header_join = " ".join(grid[0]).lower() if grid else ""
        has_table_hint = any(k in header_join for k in ("bit", "start", "end", "field", "word"))
        if has_table_hint:
            results.append({"page": p + 1, "columns": columns, "rows": grid[:50]})
    doc.close()
    return results


__all__ = ["parse_tables_from_pdf"]


