#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Python PlantUML包转换PlantUML文件为PNG
"""

import plantuml
from pathlib import Path

def convert_plantuml_files():
    """转换所有PlantUML文件为PNG"""
    fig_dir = Path("chapters/fig-0")
    puml_files = list(fig_dir.glob("*.puml"))
    
    if not puml_files:
        print("未找到PlantUML文件")
        return
    
    print(f"找到 {len(puml_files)} 个PlantUML文件")
    
    # 创建PlantUML客户端
    client = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/png/')
    
    success_count = 0
    for puml_file in puml_files:
        print(f"正在转换: {puml_file.name}")
        
        try:
            # 读取PlantUML文件内容
            with open(puml_file, 'r', encoding='utf-8') as f:
                plantuml_text = f.read()
            
            # 生成PNG文件
            png_file = puml_file.parent / f"{puml_file.stem}.png"
            client.processes(plantuml_text, png_file)
            
            if png_file.exists():
                print(f"转换成功: {png_file}")
                success_count += 1
            else:
                print(f"转换失败: PNG文件未生成")
                
        except Exception as e:
            print(f"转换失败: {e}")
    
    print(f"\n转换完成: {success_count}/{len(puml_files)} 个文件成功转换")

if __name__ == "__main__":
    convert_plantuml_files()
