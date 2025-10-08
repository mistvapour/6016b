#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成第四章跨数据链协议互操作架构设计中的三张配图
使用在线PlantUML服务
"""

import os
import requests
import base64
import zlib
from pathlib import Path
import time

def encode_plantuml(text):
    """将PlantUML文本编码为URL安全的格式"""
    # 压缩文本
    compressed = zlib.compress(text.encode('utf-8'))
    # Base64编码
    encoded = base64.b64encode(compressed).decode('ascii')
    # 转换为PlantUML URL格式
    encoded = encoded.replace('+', '-').replace('/', '_')
    return encoded

def generate_plantuml_image(puml_file, output_file):
    """使用在线PlantUML服务生成图片"""
    try:
        # 读取PlantUML文件
        with open(puml_file, 'r', encoding='utf-8') as f:
            plantuml_text = f.read()
        
        print(f"正在处理: {puml_file}")
        print(f"文件大小: {len(plantuml_text)} 字符")
        
        # 编码PlantUML文本
        encoded_text = encode_plantuml(plantuml_text)
        
        # 构建在线PlantUML URL
        url = f"http://www.plantuml.com/plantuml/png/{encoded_text}"
        
        print(f"正在生成图片...")
        
        # 发送请求
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            # 保存图片
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"✓ 成功生成图片: {output_file}")
            print(f"图片大小: {len(response.content)} 字节")
            return True
        else:
            print(f"✗ 生成图片失败: {puml_file}")
            print(f"HTTP状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"✗ 请求超时: {puml_file}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ 网络请求错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 生成图片时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("重新生成第四章跨数据链协议互操作架构设计配图")
    print("=" * 70)
    
    # 定义要生成的图片文件
    figures_dir = Path("chapters/fig-0")
    plantuml_files = [
        ("multi_protocol_support_system.puml", "multi_protocol_support_system.png"),
        ("cdm_four_layer_model.puml", "cdm_four_layer_model.png"), 
        ("semantic_interop_system.puml", "semantic_interop_system.png")
    ]
    
    success_count = 0
    total_count = len(plantuml_files)
    
    for i, (puml_name, png_name) in enumerate(plantuml_files, 1):
        puml_file = figures_dir / puml_name
        png_file = figures_dir / png_name
        
        print(f"\n[{i}/{total_count}] 处理文件: {puml_name}")
        print("-" * 50)
        
        if puml_file.exists():
            if generate_plantuml_image(puml_file, png_file):
                success_count += 1
            # 添加延迟避免请求过快
            if i < total_count:
                print("等待2秒...")
                time.sleep(2)
        else:
            print(f"✗ 文件不存在: {puml_file}")
    
    print("\n" + "=" * 70)
    print(f"生成完成: {success_count}/{total_count} 张图片成功生成")
    print("=" * 70)
    
    if success_count == total_count:
        print("✓ 所有图片生成成功！")
        print("\n生成的图片文件:")
        for _, png_name in plantuml_files:
            png_file = figures_dir / png_name
            if png_file.exists():
                size = png_file.stat().st_size
                print(f"  - {png_name} ({size} 字节)")
    else:
        print("⚠ 部分图片生成失败，请检查错误信息")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 确认PlantUML文件格式正确")
        print("3. 稍后重试")

if __name__ == "__main__":
    main()