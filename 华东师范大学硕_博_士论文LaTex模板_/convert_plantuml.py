#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlantUML转PNG脚本
将PlantUML源码文件转换为PNG图片
"""

import os
import subprocess
import sys
from pathlib import Path

def install_plantuml():
    """安装PlantUML依赖"""
    try:
        # 检查是否已安装plantuml
        result = subprocess.run(['plantuml', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("PlantUML已安装")
            return True
    except FileNotFoundError:
        pass
    
    print("正在安装PlantUML...")
    try:
        # 尝试通过pip安装
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'plantuml'], 
                      check=True)
        print("PlantUML安装成功")
        return True
    except subprocess.CalledProcessError:
        print("PlantUML安装失败，请手动安装")
        return False

def convert_plantuml_to_png(puml_file, output_dir=None):
    """将PlantUML文件转换为PNG"""
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
        # 使用plantuml命令行工具转换
        cmd = ['plantuml', '-tpng', '-o', str(output_dir), str(puml_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            png_file = output_dir / f"{puml_path.stem}.png"
            if png_file.exists():
                print(f"转换成功: {png_file}")
                return True
            else:
                print(f"PNG文件未生成: {png_file}")
                return False
        else:
            print(f"转换失败: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("PlantUML未安装或不在PATH中")
        return False
    except Exception as e:
        print(f"转换过程中出错: {e}")
        return False

def convert_all_plantuml_files(directory):
    """转换目录中的所有PlantUML文件"""
    directory = Path(directory)
    puml_files = list(directory.glob("*.puml"))
    
    if not puml_files:
        print(f"在目录 {directory} 中未找到.puml文件")
        return
    
    print(f"找到 {len(puml_files)} 个PlantUML文件")
    
    success_count = 0
    for puml_file in puml_files:
        print(f"\n正在转换: {puml_file.name}")
        if convert_plantuml_to_png(puml_file):
            success_count += 1
    
    print(f"\n转换完成: {success_count}/{len(puml_files)} 个文件成功转换")

def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    fig_dir = script_dir / "chapters" / "fig-0"
    
    print("PlantUML转PNG工具")
    print("=" * 50)
    
    # 检查PlantUML是否安装
    if not install_plantuml():
        print("请先安装PlantUML:")
        print("1. 下载PlantUML jar文件")
        print("2. 安装Java运行环境")
        print("3. 将plantuml.jar添加到PATH")
        return
    
    # 转换所有PlantUML文件
    if fig_dir.exists():
        convert_all_plantuml_files(fig_dir)
    else:
        print(f"目录不存在: {fig_dir}")
    
    print("\n转换完成！")

if __name__ == "__main__":
    main()
