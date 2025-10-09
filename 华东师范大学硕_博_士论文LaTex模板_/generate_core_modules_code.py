#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成核心功能模块实现代码图
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置图片保存路径
output_dir = "chapters/fig-0"
os.makedirs(output_dir, exist_ok=True)

def create_core_modules_code():
    """生成核心功能模块实现代码图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 模拟代码结构
    code_lines = [
        "# 核心功能模块实现",
        "",
        "class PDFProcessor:",
        "    \"\"\"PDF文档处理模块\"\"\"",
        "    def __init__(self):",
        "        self.pdf_tools = ['PyMuPDF', 'pdfplumber', 'Camelot']",
        "        self.ocr_engine = 'Tesseract OCR'",
        "        self.pipeline = ['文档解析', '表格识别', '章节解析', 'SIM构建']",
        "    ",
        "    def extract_data(self, pdf_path):",
        "        \"\"\"从PDF文档中提取结构化数据\"\"\"",
        "        # 文档解析 → 表格识别 → 章节解析",
        "        structured_data = self._parse_document(pdf_path)",
        "        tables = self._extract_tables(structured_data)",
        "        sections = self._parse_sections(structured_data)",
        "        return self._build_sim(tables, sections)",
        "",
        "class SemanticInterop:",
        "    \"\"\"语义互操作模块\"\"\"",
        "    def __init__(self):",
        "        self.ml_model = SemanticAnalyzer()",
        "        self.mapping_rules = MappingRuleEngine()",
        "        self.protocols = ['Link16', 'JREAP', 'TTNT']",
        "    ",
        "    def analyze_semantics(self, message):",
        "        \"\"\"分析消息语义并建立映射关系\"\"\"",
        "        # 消息语义分析 → 跨协议转换",
        "        semantic_features = self.ml_model.extract_features(message)",
        "        mapping = self.mapping_rules.find_mapping(semantic_features)",
        "        return self._convert_protocol(message, mapping)",
        "",
        "class CDMConverter:",
        "    \"\"\"CDM四层法转换模块\"\"\"",
        "    def __init__(self):",
        "        self.layers = {",
        "            'semantic': SemanticLayer(),",
        "            'mapping': MappingLayer(),",
        "            'validation': ValidationLayer(),",
        "            'runtime': RuntimeLayer()",
        "        }",
        "    ",
        "    def convert_protocol(self, source, target):",
        "        \"\"\"三段式协议转换：源协议 → CDM → 目标协议\"\"\"",
        "        # 源协议 → CDM → 目标协议",
        "        cdm_data = self.layers['semantic'].to_cdm(source)",
        "        validated_data = self.layers['validation'].validate(cdm_data)",
        "        return self.layers['runtime'].to_target(validated_data, target)",
        "",
        "class UniversalImporter:",
        "    \"\"\"统一导入模块\"\"\"",
        "    def __init__(self):",
        "        self.supported_formats = ['PDF', 'XML', 'CSV', 'JSON']",
        "        self.adapters = {",
        "            'PDF': PDFAdapter(),",
        "            'XML': XMLAdapter(),",
        "            'CSV': CSVAdapter()",
        "        }",
        "    ",
        "    def auto_detect_format(self, file_path):",
        "        \"\"\"自动检测文件格式并选择适配器\"\"\"",
        "        # 格式检测 → 适配器选择 → 数据处理",
        "        file_format = self._detect_format(file_path)",
        "        adapter = self.adapters.get(file_format)",
        "        if adapter:",
        "            return adapter.process(file_path)",
        "        else:",
        "            raise UnsupportedFormatError(f'不支持的文件格式: {file_format}')",
        "",
        "    def batch_import(self, file_list):",
        "        \"\"\"批量导入多个文件\"\"\"",
        "        results = []",
        "        for file_path in file_list:",
        "            try:",
        "                result = self.auto_detect_format(file_path)",
        "                results.append(result)",
        "            except Exception as e:",
        "                logger.error(f'导入文件失败 {file_path}: {e}')",
        "        return results"
    ]
    
    # 绘制代码背景
    ax.add_patch(Rectangle((0.02, 0.02), 0.96, 0.96, 
                          facecolor='#1e1e1e', edgecolor='#333333', linewidth=2))
    
    # 绘制代码行
    y_pos = 0.95
    line_height = 0.025
    
    for line in code_lines:
        # 根据代码内容设置颜色
        if line.strip().startswith('#'):
            color = '#569cd6'  # 注释颜色
        elif line.strip().startswith('class '):
            color = '#4ec9b0'  # 类定义
        elif line.strip().startswith('def '):
            color = '#dcdcaa'  # 函数定义
        elif line.strip().startswith('    \"\"\"'):
            color = '#6a9955'  # 文档字符串
        elif line.strip().startswith('    #'):
            color = '#569cd6'  # 行内注释
        elif line.strip().startswith('    '):
            color = '#dcdcdc'  # 缩进代码
        elif line.strip().startswith('        '):
            color = '#ce9178'  # 深层缩进
        else:
            color = '#dcdcdc'  # 普通文本
            
        ax.text(0.05, y_pos, line, fontsize=9, color=color, 
                fontfamily='monospace', va='top')
        y_pos -= line_height
    
    # 添加标题和说明
    ax.text(0.5, 0.98, '核心功能模块实现代码', 
            ha='center', va='top', fontsize=16, fontweight='bold', color='white')
    
    # 添加模块说明
    module_info = [
        "PDFProcessor: 集成PyMuPDF、pdfplumber、Camelot等工具",
        "SemanticInterop: 基于机器学习的语义分析和跨协议转换",
        "CDMConverter: 四层架构的协议转换引擎",
        "UniversalImporter: 支持多格式的智能导入系统"
    ]
    
    info_y = 0.02
    for info in module_info:
        ax.text(0.05, info_y, f"• {info}", fontsize=8, color='#888888', va='bottom')
        info_y += 0.015
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/core_modules_code.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"核心功能模块代码图已保存到: {output_dir}/core_modules_code.png")

if __name__ == "__main__":
    create_core_modules_code()
