#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UML转换器
"""

import subprocess
import sys
from pathlib import Path

def test_plantuml_with_jar():
    """使用jar文件测试PlantUML转换"""
    jar_path = Path("华东师范大学硕_博_士论文LaTex模板_/plantuml.jar")
    test_puml = Path("华东师范大学硕_博_士论文LaTex模板_/chapters/fig-0/semantic_interop_system.puml")
    output_dir = Path("./test_output")
    
    if not jar_path.exists():
        print(f"PlantUML jar文件不存在: {jar_path}")
        return False
    
    if not test_puml.exists():
        print(f"测试文件不存在: {test_puml}")
        return False
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    try:
        # 使用Java运行PlantUML jar
        cmd = [
            'java',
            '-jar', str(jar_path),
            '-tpng',
            '-o', str(output_dir),
            str(test_puml)
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            png_file = output_dir / f"{test_puml.stem}.png"
            if png_file.exists():
                print(f"转换成功: {png_file}")
                print(f"文件大小: {png_file.stat().st_size} 字节")
                return True
            else:
                print(f"PNG文件未生成: {png_file}")
                return False
        else:
            print(f"转换失败:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("转换超时")
        return False
    except Exception as e:
        print(f"转换过程中出错: {e}")
        return False

def test_java_available():
    """测试Java是否可用"""
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Java可用:")
            print(result.stderr)  # Java版本信息通常在stderr中
            return True
        else:
            print("Java不可用")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Java未安装或不在PATH中")
        return False

def main():
    """主测试函数"""
    print("UML转换器测试")
    print("=" * 50)
    
    # 测试Java
    print("\n1. 测试Java环境...")
    if not test_java_available():
        print("请先安装Java运行环境")
        return
    
    # 测试PlantUML转换
    print("\n2. 测试PlantUML转换...")
    if test_plantuml_with_jar():
        print("✅ PlantUML转换测试成功")
    else:
        print("❌ PlantUML转换测试失败")

if __name__ == "__main__":
    main()
