#!/usr/bin/env python3
"""
分析PDF文件内容
"""
import re
from pathlib import Path

def analyze_pdf():
    """分析PDF文件"""
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print(f"分析PDF文件: {pdf_path}")
    print(f"文件大小: {Path(pdf_path).stat().st_size} bytes")
    
    # 读取PDF内容
    with open(pdf_path, 'rb') as f:
        content = f.read()
    
    # 转换为文本
    text = content.decode('latin-1', errors='ignore')
    
    print("\n=== PDF内容分析 ===")
    
    # 查找J消息模式
    j_patterns = re.findall(r'J\d+(?:\.\d+)?', text)
    print(f"J消息模式: {j_patterns}")
    
    # 查找表格关键词
    keywords = ['word', 'bit', 'field', 'description', 'start', 'end']
    found = [k for k in keywords if k.lower() in text.lower()]
    print(f"表格关键词: {found}")
    
    # 查找位段模式
    bit_patterns = re.findall(r'\d+\s*[-–~\.]{1,2}\s*\d+', text)
    print(f"位段模式: {bit_patterns}")
    
    # 查找单位
    units = re.findall(r'\b(deg|rad|ft|m|kts|m/s)\b', text, re.IGNORECASE)
    print(f"单位: {units}")
    
    # 查找DFI/DUI/DI
    dfi = re.findall(r'DFI\s*\d+', text, re.IGNORECASE)
    dui = re.findall(r'DUI\s*\d+', text, re.IGNORECASE)
    di = re.findall(r'DI\s*[:：]', text, re.IGNORECASE)
    print(f"DFI: {dfi}")
    print(f"DUI: {dui}")
    print(f"DI: {di}")
    
    # 提取可读文本
    readable = ''.join(c for c in text if c.isprintable() and c not in '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f')
    
    print(f"\n可读文本预览 (前200字符):")
    print(readable[:200])
    
    if len(readable) > 200:
        print("...")

if __name__ == "__main__":
    analyze_pdf()
