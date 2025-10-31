#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plantuml import PlantUML
from pathlib import Path

def convert_plantuml_to_png(puml_file):
    """转换PlantUML文件为PNG图片"""
    plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')
    
    try:
        with open(puml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = plantuml.processes(content)
        
        png_file = puml_file.replace('.puml', '.png')
        with open(png_file, 'wb') as f:
            f.write(result)
        
        print(f'✅ 转换成功: {Path(puml_file).name} -> {Path(png_file).name}')
        print(f'文件大小: {len(result)} bytes')
        return True
        
    except Exception as e:
        print(f'❌ 转换失败 {Path(puml_file).name}: {str(e)}')
        return False

def main():
    """主函数：转换所有微服务架构图"""
    base_path = Path('chapters/fig-0')
    
    # 要转换的PlantUML文件列表
    puml_files = [
        'microservice_deployment.puml',
        'data_management.puml', 
        'monitoring_fault_tolerance.puml'
    ]
    
    print("🚀 开始转换微服务架构图...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(puml_files)
    
    for puml_file in puml_files:
        puml_path = base_path / puml_file
        if puml_path.exists():
            if convert_plantuml_to_png(str(puml_path)):
                success_count += 1
            print("-" * 30)
        else:
            print(f'❌ 文件不存在: {puml_file}')
            print("-" * 30)
    
    print("=" * 50)
    print(f"📊 转换完成: {success_count}/{total_count} 个文件成功转换")
    
    if success_count == total_count:
        print("🎉 所有图表转换成功！")
    else:
        print("⚠️  部分图表转换失败，请检查错误信息")

if __name__ == "__main__":
    main()
