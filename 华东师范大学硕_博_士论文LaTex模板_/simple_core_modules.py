#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的核心功能模块代码图生成
"""

import os

# 设置图片保存路径
output_dir = "chapters/fig-0"
os.makedirs(output_dir, exist_ok=True)

print("开始生成核心功能模块代码图...")

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图形
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 简化的代码结构
    code_lines = [
        "# 核心功能模块实现",
        "",
        "class PDFProcessor:",
        "    def __init__(self):",
        "        self.pdf_tools = ['PyMuPDF', 'pdfplumber', 'Camelot']",
        "        self.ocr_engine = 'Tesseract OCR'",
        "    ",
        "    def extract_data(self, pdf_path):",
        "        # 文档解析 → 表格识别 → 章节解析",
        "        return structured_data",
        "",
        "class SemanticInterop:",
        "    def __init__(self):",
        "        self.ml_model = SemanticAnalyzer()",
        "    ",
        "    def analyze_semantics(self, message):",
        "        # 消息语义分析 → 跨协议转换",
        "        return semantic_mapping",
        "",
        "class CDMConverter:",
        "    def __init__(self):",
        "        self.layers = ['语义层', '映射层', '校验层', '运行层']",
        "    ",
        "    def convert_protocol(self, source, target):",
        "        # 源协议 → CDM → 目标协议",
        "        return converted_data",
        "",
        "class UniversalImporter:",
        "    def __init__(self):",
        "        self.supported_formats = ['PDF', 'XML', 'CSV']",
        "    ",
        "    def auto_detect_format(self, file_path):",
        "        # 格式检测 → 适配器选择 → 数据处理",
        "        return processed_data"
    ]
    
    # 绘制代码背景
    ax.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, 
                          facecolor='#1e1e1e', edgecolor='#333333', linewidth=2))
    
    # 绘制代码行
    y_pos = 0.9
    for line in code_lines:
        if line.strip().startswith('#'):
            color = '#569cd6'  # 注释颜色
        elif line.strip().startswith('class') or line.strip().startswith('def'):
            color = '#4ec9b0'  # 关键字颜色
        elif line.strip().startswith('    '):
            color = '#dcdcdc'  # 缩进代码颜色
        else:
            color = '#dcdcdc'  # 普通文本颜色
            
        ax.text(0.08, y_pos, line, fontsize=10, color=color, 
                fontfamily='monospace', va='top')
        y_pos -= 0.04
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('核心功能模块实现代码', fontsize=16, fontweight='bold', pad=20)
    
    # 保存图片
    plt.tight_layout()
    plt.savefig(f"{output_dir}/core_modules_code.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"核心功能模块代码图已保存到: {output_dir}/core_modules_code.png")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请安装matplotlib: pip install matplotlib")
except Exception as e:
    print(f"生成图片时出错: {e}")

print("脚本执行完成")
