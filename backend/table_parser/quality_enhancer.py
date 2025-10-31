#!/usr/bin/env python3
"""
表格质量优化模块：
- 增强表头识别（模糊匹配/ML分类）
- 列对齐优化（x轴投影聚类）
- 合并单元格检测与处理
- 噪声过滤与置信度评分
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import re
from collections import Counter


@dataclass
class TableQuality:
    confidence: float
    header_score: float
    alignment_score: float
    noise_score: float
    issues: List[str]


@dataclass
class EnhancedCell:
    text: str
    x0: float
    x1: float
    y0: float
    y1: float
    row_span: int = 1
    col_span: int = 1
    confidence: float = 1.0


class TableQualityEnhancer:
    def __init__(self):
        # 扩展表头关键词
        self.header_keywords = {
            "field": {"field", "字段", "name", "项", "参数", "参数名", "field_name"},
            "start": {"start", "起始", "begin", "from", "start_bit", "起始位"},
            "end": {"end", "结束", "to", "end_bit", "结束位"},
            "bit": {"bit", "bits", "位", "位段", "bit_range", "位范围"},
            "units": {"units", "单位", "unit", "measurement"},
            "description": {"description", "desc", "说明", "描述", "comment", "备注"},
            "type": {"type", "类型", "dtype", "data_type"},
            "value": {"value", "值", "default", "默认值"},
        }
        
        # 噪声模式
        self.noise_patterns = [
            r"^\d+$",  # 纯数字
            r"^[^\w\u4e00-\u9fff]+$",  # 纯符号
            r"^[a-z]{1,2}$",  # 单字母
        ]
    
    def enhance_table_detection(self, spans: List[Tuple[str, Tuple[float, float, float, float]]]) -> List[EnhancedCell]:
        """增强表格检测，返回带置信度的单元格"""
        if not spans:
            return []
        
        # 1. 转换为EnhancedCell
        cells = []
        for text, (x0, y0, x1, y1) in spans:
            cell = EnhancedCell(
                text=text.strip(),
                x0=x0, x1=x1, y0=y0, y1=y1,
                confidence=self._calculate_cell_confidence(text)
            )
            cells.append(cell)
        
        # 2. 行聚类（优化y轴容差）
        rows = self._cluster_rows_enhanced(cells)
        
        # 3. 列对齐优化
        columns = self._optimize_column_alignment(rows)
        
        # 4. 合并单元格检测
        merged_cells = self._detect_merged_cells(rows, columns)
        
        return merged_cells
    
    def _calculate_cell_confidence(self, text: str) -> float:
        """计算单元格置信度"""
        if not text:
            return 0.0
        
        # 噪声检测
        for pattern in self.noise_patterns:
            if re.match(pattern, text):
                return 0.3
        
        # 长度合理性
        if len(text) < 2:
            return 0.5
        if len(text) > 100:
            return 0.7
        
        # 包含关键词加分
        text_lower = text.lower()
        keyword_bonus = 0
        for category, keywords in self.header_keywords.items():
            if any(kw in text_lower for kw in keywords):
                keyword_bonus += 0.2
        
        return min(1.0, 0.8 + keyword_bonus)
    
    def _cluster_rows_enhanced(self, cells: List[EnhancedCell]) -> List[List[EnhancedCell]]:
        """增强行聚类，考虑y轴重叠"""
        if not cells:
            return []
        
        # 按y0排序
        cells_sorted = sorted(cells, key=lambda c: (c.y0, c.x0))
        
        rows = []
        current_row = []
        current_y = None
        y_tolerance = 3.0  # 增加容差
        
        for cell in cells_sorted:
            if current_y is None:
                current_y = cell.y0
                current_row = [cell]
            elif abs(cell.y0 - current_y) <= y_tolerance:
                # 检查y轴重叠
                if self._has_y_overlap(cell, current_row[0]):
                    current_row.append(cell)
                else:
                    # 新行
                    rows.append(sorted(current_row, key=lambda c: c.x0))
                    current_row = [cell]
                    current_y = cell.y0
            else:
                # 新行
                rows.append(sorted(current_row, key=lambda c: c.x0))
                current_row = [cell]
                current_y = cell.y0
        
        if current_row:
            rows.append(sorted(current_row, key=lambda c: c.x0))
        
        return rows
    
    def _has_y_overlap(self, cell1: EnhancedCell, cell2: EnhancedCell) -> bool:
        """检查两个单元格是否有y轴重叠"""
        return not (cell1.y1 < cell2.y0 or cell2.y1 < cell1.y0)
    
    def _optimize_column_alignment(self, rows: List[List[EnhancedCell]]) -> List[float]:
        """优化列对齐，使用更智能的x轴投影"""
        if not rows:
            return []
        
        # 收集所有x位置
        x_positions = []
        for row in rows:
            for cell in row:
                x_positions.extend([cell.x0, cell.x1])
        
        x_positions.sort()
        
        # 使用K-means思想进行列聚类
        columns = self._cluster_x_positions(x_positions, min_gap=15.0)
        
        return columns
    
    def _cluster_x_positions(self, positions: List[float], min_gap: float) -> List[float]:
        """x位置聚类"""
        if not positions:
            return []
        
        clusters = []
        current_cluster = [positions[0]]
        
        for pos in positions[1:]:
            if pos - current_cluster[-1] <= min_gap:
                current_cluster.append(pos)
            else:
                clusters.append(current_cluster)
                current_cluster = [pos]
        
        if current_cluster:
            clusters.append(current_cluster)
        
        # 返回每个聚类的中心
        return [sum(cluster) / len(cluster) for cluster in clusters]
    
    def _detect_merged_cells(self, rows: List[List[EnhancedCell]], columns: List[float]) -> List[EnhancedCell]:
        """检测合并单元格"""
        if not rows or not columns:
            return []
        
        merged_cells = []
        
        for row in rows:
            for cell in row:
                # 计算列跨度
                col_span = self._calculate_col_span(cell, columns)
                
                # 计算行跨度（简化：检查下一行是否有相同x范围的单元格）
                row_span = self._calculate_row_span(cell, rows, columns)
                
                # 创建合并单元格
                merged_cell = EnhancedCell(
                    text=cell.text,
                    x0=cell.x0, x1=cell.x1,
                    y0=cell.y0, y1=cell.y1,
                    row_span=row_span,
                    col_span=col_span,
                    confidence=cell.confidence
                )
                merged_cells.append(merged_cell)
        
        return merged_cells
    
    def _calculate_col_span(self, cell: EnhancedCell, columns: List[float]) -> int:
        """计算列跨度"""
        if not columns:
            return 1
        
        start_col = 0
        end_col = len(columns) - 1
        
        for i, col_x in enumerate(columns):
            if cell.x0 <= col_x <= cell.x1:
                start_col = min(start_col, i)
                end_col = max(end_col, i)
        
        return max(1, end_col - start_col + 1)
    
    def _calculate_row_span(self, cell: EnhancedCell, rows: List[List[EnhancedCell]], columns: List[float]) -> int:
        """计算行跨度（简化实现）"""
        # 简化：检查下一行是否有重叠的单元格
        current_row_idx = -1
        for i, row in enumerate(rows):
            if cell in row:
                current_row_idx = i
                break
        
        if current_row_idx == -1 or current_row_idx >= len(rows) - 1:
            return 1
        
        # 检查下一行
        next_row = rows[current_row_idx + 1]
        for next_cell in next_row:
            if self._has_x_overlap(cell, next_cell):
                return 2
        
        return 1
    
    def _has_x_overlap(self, cell1: EnhancedCell, cell2: EnhancedCell) -> bool:
        """检查x轴重叠"""
        return not (cell1.x1 < cell2.x0 or cell2.x1 < cell1.x0)
    
    def assess_table_quality(self, cells: List[EnhancedCell]) -> TableQuality:
        """评估表格质量"""
        if not cells:
            return TableQuality(0.0, 0.0, 0.0, 0.0, ["No cells found"])
        
        issues = []
        
        # 1. 表头质量
        header_score = self._assess_header_quality(cells)
        if header_score < 0.5:
            issues.append("Poor header detection")
        
        # 2. 对齐质量
        alignment_score = self._assess_alignment_quality(cells)
        if alignment_score < 0.6:
            issues.append("Poor column alignment")
        
        # 3. 噪声评估
        noise_score = self._assess_noise_level(cells)
        if noise_score < 0.7:
            issues.append("High noise level")
        
        # 4. 整体置信度
        avg_confidence = sum(c.confidence for c in cells) / len(cells)
        overall_confidence = (header_score + alignment_score + noise_score) / 3
        
        return TableQuality(
            confidence=overall_confidence,
            header_score=header_score,
            alignment_score=alignment_score,
            noise_score=noise_score,
            issues=issues
        )
    
    def _assess_header_quality(self, cells: List[EnhancedCell]) -> float:
        """评估表头质量"""
        if not cells:
            return 0.0
        
        # 检查是否包含表头关键词
        header_count = 0
        for cell in cells[:10]:  # 检查前10个单元格
            text_lower = cell.text.lower()
            for category, keywords in self.header_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    header_count += 1
                    break
        
        return min(1.0, header_count / 3)  # 至少3个关键词
    
    def _assess_alignment_quality(self, cells: List[EnhancedCell]) -> float:
        """评估对齐质量"""
        if len(cells) < 2:
            return 1.0
        
        # 计算x位置的标准差
        x_positions = [c.x0 for c in cells]
        if not x_positions:
            return 0.0
        
        mean_x = sum(x_positions) / len(x_positions)
        variance = sum((x - mean_x) ** 2 for x in x_positions) / len(x_positions)
        std_dev = variance ** 0.5
        
        # 标准差越小，对齐越好
        return max(0.0, 1.0 - std_dev / 100.0)
    
    def _assess_noise_level(self, cells: List[EnhancedCell]) -> float:
        """评估噪声水平"""
        if not cells:
            return 1.0
        
        noise_count = 0
        for cell in cells:
            if cell.confidence < 0.5:
                noise_count += 1
        
        return 1.0 - (noise_count / len(cells))


__all__ = ["TableQualityEnhancer", "EnhancedCell", "TableQuality"]
