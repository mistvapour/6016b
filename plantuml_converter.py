#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlantUML转换器 - 使用Python PlantUML库
支持批量转换PlantUML文件为PNG格式
"""

import sys
import argparse
from pathlib import Path
from plantuml import PlantUML

def convert_plantuml_to_png(puml_file, output_file=None, server_url='http://www.plantuml.com/plantuml/png/'):
    """
    转换单个PlantUML文件为PNG
    
    Args:
        puml_file: PlantUML源文件路径
        output_file: 输出PNG文件路径（可选，默认替换扩展名）
        server_url: PlantUML服务器URL
    
    Returns:
        bool: 转换是否成功
    """
    try:
        puml_path = Path(puml_file)
        if not puml_path.exists():
            print(f"❌ 文件不存在: {puml_file}")
            return False
        
        # 如果没有指定输出文件，自动生成
        if output_file is None:
            output_file = puml_path.with_suffix('.png')
        else:
            output_file = Path(output_file)
        
        # 创建PlantUML实例
        plantuml = PlantUML(url=server_url)
        
        # 读取PlantUML源码
        with open(puml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 转换并保存
        result = plantuml.processes(content)
        with open(output_file, 'wb') as f:
            f.write(result)
        
        print(f"✅ 转换成功: {puml_path.name} -> {output_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败 {puml_path.name}: {e}")
        return False

def batch_convert(directory, pattern="*.puml", recursive=False):
    """
    批量转换目录中的PlantUML文件
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        recursive: 是否递归搜索子目录
    
    Returns:
        tuple: (成功数量, 总数量)
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"❌ 目录不存在: {directory}")
        return 0, 0
    
    # 查找PlantUML文件
    if recursive:
        puml_files = list(dir_path.rglob(pattern))
    else:
        puml_files = list(dir_path.glob(pattern))
    
    if not puml_files:
        print(f"❌ 在目录 {directory} 中未找到匹配 {pattern} 的文件")
        return 0, 0
    
    print(f"📁 找到 {len(puml_files)} 个PlantUML文件")
    
    success_count = 0
    for puml_file in puml_files:
        if convert_plantuml_to_png(puml_file):
            success_count += 1
    
    print(f"\n📊 批量转换完成: {success_count}/{len(puml_files)} 成功")
    return success_count, len(puml_files)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PlantUML转PNG转换器')
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='输出文件路径（单文件模式）')
    parser.add_argument('-p', '--pattern', default='*.puml', help='文件匹配模式（批量模式）')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归搜索子目录')
    parser.add_argument('-s', '--server', default='http://www.plantuml.com/plantuml/png/', 
                       help='PlantUML服务器URL')
    parser.add_argument('--batch', action='store_true', help='批量转换模式')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"❌ 输入路径不存在: {args.input}")
        return
    
    if args.batch or input_path.is_dir():
        # 批量转换模式
        print("🔄 批量转换模式")
        success, total = batch_convert(args.input, args.pattern, args.recursive)
        if success == total:
            print("🎉 所有文件转换成功！")
        else:
            print(f"⚠️  {total - success} 个文件转换失败")
    else:
        # 单文件转换模式
        print("🔄 单文件转换模式")
        if convert_plantuml_to_png(args.input, args.output, args.server):
            print("🎉 转换成功！")
        else:
            print("❌ 转换失败")

if __name__ == "__main__":
    main()
