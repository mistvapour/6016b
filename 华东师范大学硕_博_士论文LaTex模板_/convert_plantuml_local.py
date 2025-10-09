#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlantUML转PNG脚本（使用Python plantuml库）
将PlantUML源码文件转换为PNG图片
"""

import os
import sys
from pathlib import Path

def install_plantuml():
    """安装PlantUML依赖"""
    try:
        import plantuml
        print("PlantUML库已安装")
        return True
    except ImportError:
        print("正在安装PlantUML库...")
        try:
            import subprocess
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'plantuml'], 
                          check=True)
            print("PlantUML库安装成功")
            return True
        except subprocess.CalledProcessError:
            print("PlantUML库安装失败")
            return False

def convert_plantuml_to_png(puml_file, output_dir=None):
    """将PlantUML文件转换为PNG"""
    try:
        from plantuml import PlantUML
    except ImportError:
        print("PlantUML库未安装")
        return False
    
    puml_path = Path(puml_file)
    if not puml_path.exists():
        print(f"文件不存在: {puml_file}")
        return False
    
    if output_dir is None:
        output_dir = puml_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 读取PlantUML文件内容
        with open(puml_path, 'r', encoding='utf-8') as f:
            plantuml_text = f.read()
        
        # 使用PlantUML在线服务
        plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')
        
        # 生成PNG
        png_data = plantuml.processes(plantuml_text)
        
        # 保存PNG文件
        png_file = output_dir / f"{puml_path.stem}.png"
        with open(png_file, 'wb') as f:
            f.write(png_data)
        
        print(f"转换成功: {png_file}")
        return True
        
    except Exception as e:
        print(f"转换过程中出错: {e}")
        return False

def convert_specific_files():
    """转换特定的文件"""
    script_dir = Path(__file__).parent
    fig_dir = script_dir / "chapters" / "fig-0"
    
    # 要转换的文件
    target_files = [
        "import_pipeline_simple.puml"
    ]
    
    success_count = 0
    for filename in target_files:
        puml_file = fig_dir / filename
        if puml_file.exists():
            print(f"\n正在转换: {filename}")
            if convert_plantuml_to_png(puml_file):
                success_count += 1
        else:
            print(f"文件不存在: {filename}")
    
    print(f"\n转换完成: {success_count}/{len(target_files)} 个文件成功转换")

def main():
    """主函数"""
    print("PlantUML转PNG工具（本地版）")
    print("=" * 50)
    
    try:
        # 检查PlantUML是否安装
        if not install_plantuml():
            print("请先安装PlantUML库")
            return
        
        # 转换特定的三张图
        convert_specific_files()
        
        print("\n转换完成！")
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
