#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统架构图生成
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置图片保存路径
output_dir = "chapters/fig-0"
os.makedirs(output_dir, exist_ok=True)

def create_system_architecture():
    """生成系统整体架构设计图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # 定义各层的位置和大小
    layers = [
        {"name": "应用展示层\n(React 18)", "y": 0.8, "color": "#E3F2FD", "border": "#1976D2"},
        {"name": "接口服务层\n(FastAPI)", "y": 0.6, "color": "#F3E5F5", "border": "#7B1FA2"},
        {"name": "数据管理层\n(Business Logic)", "y": 0.4, "color": "#E8F5E8", "border": "#388E3C"},
        {"name": "数据存储层\n(MySQL + Redis)", "y": 0.2, "color": "#FFF3E0", "border": "#F57C00"}
    ]
    
    # 绘制各层
    for layer in layers:
        box = FancyBboxPatch(
            (0.1, layer["y"] - 0.08), 0.8, 0.12,
            boxstyle="round,pad=0.01",
            facecolor=layer["color"],
            edgecolor=layer["border"],
            linewidth=2
        )
        ax.add_patch(box)
        ax.text(0.5, layer["y"] - 0.02, layer["name"], 
                ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 添加箭头表示数据流
    arrow_props = dict(arrowstyle='->', lw=2, color='#666666')
    
    # 向下箭头
    for i in range(len(layers) - 1):
        ax.annotate('', xy=(0.5, layers[i+1]["y"] + 0.08), 
                   xytext=(0.5, layers[i]["y"] - 0.08),
                   arrowprops=arrow_props)
    
    # 添加微服务标注
    ax.text(0.05, 0.95, "微服务架构 (9个核心服务)", 
            fontsize=10, fontweight='bold', color='#1976D2')
    
    # 添加技术栈标注
    tech_stack = [
        "Python 3.10 + FastAPI",
        "React 18 + TypeScript", 
        "MySQL 8.0 + Redis",
        "Docker + Kubernetes"
    ]
    
    for i, tech in enumerate(tech_stack):
        ax.text(0.85, 0.9 - i*0.05, tech, 
                fontsize=9, color='#666666', ha='right')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('系统整体架构设计', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/system_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"系统架构图已保存到: {output_dir}/system_architecture.png")

if __name__ == "__main__":
    create_system_architecture()
