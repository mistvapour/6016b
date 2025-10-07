#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlantUML在线转换脚本
使用PlantUML在线服务将PlantUML源码转换为PNG图片
"""

import os
import requests
import base64
import zlib
from pathlib import Path
import time

def encode_plantuml(text):
    """将PlantUML文本编码为PlantUML在线服务所需的格式"""
    # 压缩文本
    compressed = zlib.compress(text.encode('utf-8'))
    # Base64编码
    encoded = base64.b64encode(compressed).decode('ascii')
    # 转换为PlantUML格式
    plantuml_encoded = ""
    for i in range(0, len(encoded), 64):
        plantuml_encoded += encoded[i:i+64] + "\n"
    return plantuml_encoded.strip()

def convert_plantuml_online(puml_file, output_dir=None):
    """使用在线服务将PlantUML文件转换为PNG"""
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
        
        # 编码文本
        encoded_text = encode_plantuml(plantuml_text)
        
        # 构建在线服务URL
        url = f"http://www.plantuml.com/plantuml/png/{encoded_text}"
        
        print(f"正在转换: {puml_path.name}")
        print(f"请求URL: {url[:100]}...")
        
        # 发送请求
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # 保存PNG文件
            png_file = output_dir / f"{puml_path.stem}.png"
            with open(png_file, 'wb') as f:
                f.write(response.content)
            print(f"转换成功: {png_file}")
            return True
        else:
            print(f"转换失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
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
    for i, puml_file in enumerate(puml_files, 1):
        print(f"\n[{i}/{len(puml_files)}] 正在转换: {puml_file.name}")
        if convert_plantuml_online(puml_file):
            success_count += 1
        
        # 添加延迟避免请求过于频繁
        if i < len(puml_files):
            time.sleep(1)
    
    print(f"\n转换完成: {success_count}/{len(puml_files)} 个文件成功转换")

def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    fig_dir = script_dir / "chapters" / "fig-0"
    
    print("PlantUML在线转换工具")
    print("=" * 50)
    
    # 转换所有PlantUML文件
    if fig_dir.exists():
        convert_all_plantuml_files(fig_dir)
    else:
        print(f"目录不存在: {fig_dir}")
    
    print("\n转换完成！")

if __name__ == "__main__":
    main()
