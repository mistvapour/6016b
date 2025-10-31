#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import base64
import zlib

def plantuml_to_png(puml_file, png_file):
    """将PlantUML文件转换为PNG图片"""
    try:
        # 读取PlantUML文件
        with open(puml_file, 'r', encoding='utf-8') as f:
            plantuml_code = f.read()
        
        # 压缩并编码PlantUML代码
        compressed = zlib.compress(plantuml_code.encode('utf-8'))
        encoded = base64.b64encode(compressed).decode('ascii')
        
        # 构建PlantUML在线服务URL
        url = f"http://www.plantuml.com/plantuml/png/{encoded}"
        
        # 下载PNG图片
        with urllib.request.urlopen(url) as response:
            png_data = response.read()
        
        # 保存PNG文件
        with open(png_file, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ 转换成功: {puml_file} -> {png_file}")
        print(f"文件大小: {len(png_data)} bytes")
        return True
        
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
    
    print("🚀 开始转换PlantUML文件...")
    success = 0
    
    for puml_file, png_file in files:
        if plantuml_to_png(puml_file, png_file):
            success += 1
    
    print(f"📊 转换完成: {success}/{len(files)} 个文件成功")

if __name__ == "__main__":
    main()