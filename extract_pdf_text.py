#!/usr/bin/env python3
"""
提取PDF文件中的实际文本内容
"""
import sys
from pathlib import Path

# 尝试导入PyMuPDF
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("警告: 未安装PyMuPDF，将使用基础方法")

def extract_text_with_pymupdf(pdf_path):
    """使用PyMuPDF提取PDF文本"""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        print(f"PDF页数: {len(doc)}")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                full_text += f"\n--- 第 {page_num + 1} 页 ---\n"
                full_text += text
                full_text += "\n"
        
        doc.close()
        return full_text
        
    except Exception as e:
        print(f"PyMuPDF提取失败: {e}")
        return None

def extract_text_basic(pdf_path):
    """使用基础方法提取PDF文本"""
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        # 转换为文本
        text = content.decode('latin-1', errors='ignore')
        
        # 提取可读文本
        readable_chars = []
        for char in text:
            if char.isprintable() and ord(char) < 128:
                readable_chars.append(char)
            elif char in ['\n', '\r', '\t', ' ']:
                readable_chars.append(char)
        
        readable_text = ''.join(readable_chars)
        
        # 查找中文内容
        import re
        chinese_text = re.findall(r'[\u4e00-\u9fff]+', text)
        
        return readable_text, chinese_text
        
    except Exception as e:
        print(f"基础提取失败: {e}")
        return None, None

def analyze_extracted_text(text):
    """分析提取的文本"""
    if not text:
        return {}
    
    analysis = {
        "text_length": len(text),
        "lines": len(text.split('\n')),
        "words": len(text.split()),
    }
    
    # 查找关键词
    keywords = {
        "data_link": ["数据链", "消息", "模拟", "客户端", "开发", "测试"],
        "technical": ["MIL-STD", "6016", "Link16", "J消息", "位段", "字段", "编码"],
        "document": ["文档", "报告", "说明", "指南", "手册", "规范"],
        "system": ["系统", "架构", "设计", "实现", "功能", "模块"],
        "testing": ["测试", "验证", "调试", "运行", "执行"],
        "j_messages": ["J0", "J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9"]
    }
    
    found_keywords = {}
    text_lower = text.lower()
    
    for category, words in keywords.items():
        found = []
        for word in words:
            if word.lower() in text_lower:
                found.append(word)
        if found:
            found_keywords[category] = found
    
    analysis["keywords"] = found_keywords
    
    # 查找J消息模式
    import re
    j_patterns = re.findall(r'J\d+(?:\.\d+)?', text, re.IGNORECASE)
    if j_patterns:
        analysis["j_messages"] = list(set(j_patterns))
    
    # 查找表格相关
    table_keywords = ['word', 'bit', 'field', 'description', 'start', 'end', 'resolution', 'units']
    found_table_keywords = [kw for kw in table_keywords if kw.lower() in text_lower]
    if found_table_keywords:
        analysis["table_keywords"] = found_table_keywords
    
    return analysis

def main():
    """主函数"""
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    
    print("=" * 80)
    print("PDF文本内容提取")
    print("=" * 80)
    print(f"目标文件: {Path(pdf_path).name}")
    
    # 创建输出目录
    output_dir = Path("pdf_text_output")
    output_dir.mkdir(exist_ok=True)
    
    extracted_text = None
    
    # 尝试使用PyMuPDF提取
    if HAS_PYMUPDF:
        print("\n使用PyMuPDF提取文本...")
        extracted_text = extract_text_with_pymupdf(pdf_path)
        
        if extracted_text:
            print(f"✓ 成功提取文本，长度: {len(extracted_text)} 字符")
            
            # 保存完整文本
            text_file = output_dir / "extracted_text.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"✓ 完整文本已保存到: {text_file}")
            
            # 分析文本
            analysis = analyze_extracted_text(extracted_text)
            
            # 保存分析结果
            analysis_file = output_dir / "text_analysis.json"
            import json
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"✓ 文本分析已保存到: {analysis_file}")
            
            # 显示分析结果
            print(f"\n文本分析结果:")
            print(f"  文本长度: {analysis['text_length']:,} 字符")
            print(f"  行数: {analysis['lines']:,}")
            print(f"  单词数: {analysis['words']:,}")
            
            if 'keywords' in analysis:
                print(f"\n关键词分析:")
                for category, words in analysis['keywords'].items():
                    print(f"  {category}: {', '.join(words)}")
            
            if 'j_messages' in analysis:
                print(f"\nJ消息模式: {', '.join(analysis['j_messages'])}")
            
            if 'table_keywords' in analysis:
                print(f"表格关键词: {', '.join(analysis['table_keywords'])}")
            
            # 显示文本预览
            preview_length = 2000
            if len(extracted_text) > preview_length:
                preview = extracted_text[:preview_length] + "..."
            else:
                preview = extracted_text
            
            print(f"\n文本预览:")
            print("-" * 50)
            print(preview)
            print("-" * 50)
    
    # 如果PyMuPDF失败，使用基础方法
    if not extracted_text:
        print("\n使用基础方法提取文本...")
        readable_text, chinese_text = extract_text_basic(pdf_path)
        
        if readable_text:
            print(f"✓ 提取到可读文本，长度: {len(readable_text)} 字符")
            
            # 保存可读文本
            readable_file = output_dir / "readable_text.txt"
            with open(readable_file, 'w', encoding='utf-8') as f:
                f.write(readable_text)
            print(f"✓ 可读文本已保存到: {readable_file}")
            
            if chinese_text:
                print(f"✓ 提取到中文内容，片段数: {len(chinese_text)}")
                
                # 保存中文内容
                chinese_file = output_dir / "chinese_content.txt"
                with open(chinese_file, 'w', encoding='utf-8') as f:
                    for i, content in enumerate(chinese_text, 1):
                        f.write(f"{i}. {content}\n")
                print(f"✓ 中文内容已保存到: {chinese_file}")
                
                # 显示中文内容预览
                print(f"\n中文内容预览:")
                for i, content in enumerate(chinese_text[:10], 1):
                    print(f"  {i}. {content}")
    
    print(f"\n" + "=" * 80)
    print("文本提取完成!")
    print("=" * 80)
    print("生成的文件:")
    for file in output_dir.glob("*"):
        print(f"  - {file.name} ({file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()

