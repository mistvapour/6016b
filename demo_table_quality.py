#!/usr/bin/env python3
"""
表格质量优化演示
"""
from pathlib import Path
import json
from backend.table_parser.pymupdf_tables import parse_tables_from_pdf
from backend.table_parser.quality_enhancer import TableQualityEnhancer


def main():
    print("== 表格质量优化演示 ==")
    
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    
    # 1. 解析表格
    tables = parse_tables_from_pdf(pdf_path)
    print(f"检测到表格页数: {len(tables)}")
    
    if not tables:
        print("未检测到表格")
        return
    
    # 2. 质量优化
    enhancer = TableQualityEnhancer()
    
    for table in tables:
        page = table["page"]
        rows = table["rows"]
        
        print(f"\n--- 第 {page} 页 ---")
        print(f"原始行数: {len(rows)}")
        
        # 转换为spans格式（模拟）
        spans = []
        for row_idx, row in enumerate(rows):
            for col_idx, cell_text in enumerate(row):
                if cell_text.strip():
                    # 模拟bbox（实际应从PyMuPDF获取）
                    x0 = col_idx * 100
                    x1 = (col_idx + 1) * 100
                    y0 = row_idx * 20
                    y1 = (row_idx + 1) * 20
                    spans.append((cell_text, (x0, y0, x1, y1)))
        
        # 质量增强
        enhanced_cells = enhancer.enhance_table_detection(spans)
        
        # 质量评估
        quality = enhancer.assess_table_quality(enhanced_cells)
        
        print(f"增强后单元格数: {len(enhanced_cells)}")
        print(f"整体置信度: {quality.confidence:.3f}")
        print(f"表头质量: {quality.header_score:.3f}")
        print(f"对齐质量: {quality.alignment_score:.3f}")
        print(f"噪声水平: {quality.noise_score:.3f}")
        
        if quality.issues:
            print(f"问题: {', '.join(quality.issues)}")
        
        # 显示前几个单元格
        print("前5个单元格:")
        for i, cell in enumerate(enhanced_cells[:5]):
            print(f"  {i+1}. '{cell.text}' (置信度: {cell.confidence:.2f}, 列跨度: {cell.col_span})")
    
    # 3. 导出结果
    output_dir = Path("table_quality_output")
    output_dir.mkdir(exist_ok=True)
    
    results = []
    for table in tables:
        page = table["page"]
        rows = table["rows"]
        
        # 模拟spans
        spans = []
        for row_idx, row in enumerate(rows):
            for col_idx, cell_text in enumerate(row):
                if cell_text.strip():
                    x0 = col_idx * 100
                    x1 = (col_idx + 1) * 100
                    y0 = row_idx * 20
                    y1 = (row_idx + 1) * 20
                    spans.append((cell_text, (x0, y0, x1, y1)))
        
        enhanced_cells = enhancer.enhance_table_detection(spans)
        quality = enhancer.assess_table_quality(enhanced_cells)
        
        results.append({
            "page": page,
            "original_rows": len(rows),
            "enhanced_cells": len(enhanced_cells),
            "quality": {
                "confidence": quality.confidence,
                "header_score": quality.header_score,
                "alignment_score": quality.alignment_score,
                "noise_score": quality.noise_score,
                "issues": quality.issues
            },
            "cells": [
                {
                    "text": cell.text,
                    "confidence": cell.confidence,
                    "col_span": cell.col_span,
                    "row_span": cell.row_span
                }
                for cell in enhanced_cells[:10]  # 只保存前10个
            ]
        })
    
    # 保存结果
    output_file = output_dir / "quality_assessment.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    print("== 完成 ==")


if __name__ == "__main__":
    main()
