#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
from pathlib import Path

def convert_with_jar(puml_file, png_file):
    """使用本地PlantUML JAR文件转换"""
    try:
        # 检查JAR文件是否存在
        jar_file = "plantuml.jar"
        if not os.path.exists(jar_file):
            print(f"❌ JAR文件不存在: {jar_file}")
            return False
        
        # 使用Java运行PlantUML JAR
        cmd = ["java", "-jar", jar_file, "-tpng", puml_file]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 检查PNG文件是否生成
            if os.path.exists(png_file):
                size = os.path.getsize(png_file)
                print(f"✅ 转换成功: {Path(puml_file).name} -> {Path(png_file).name}")
                print(f"文件大小: {size} bytes")
                return True
            else:
                print(f"❌ PNG文件未生成: {png_file}")
                return False
        else:
            print(f"❌ 转换失败: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Java未安装或不在PATH中")
        return False
    except Exception as e:
        print(f"❌ 转换失败 {puml_file}: {str(e)}")
        return False

def main():
    """主函数"""
    files = [
        ('chapters/fig-0/microservice_deployment.puml', 'chapters/fig-0/microservice_deployment.png'),
        ('chapters/fig-0/data_management.puml', 'chapters/fig-0/data_management.png'),
        ('chapters/fig-0/monitoring_fault_tolerance.puml', 'chapters/fig-0/monitoring_fault_tolerance.png')
    ]
    
    print("🚀 开始使用本地JAR转换PlantUML文件...")
    success = 0
    
    for puml_file, png_file in files:
        if convert_with_jar(puml_file, png_file):
            success += 1
    
    print(f"📊 转换完成: {success}/{len(files)} 个文件成功")

if __name__ == "__main__":
    main()
