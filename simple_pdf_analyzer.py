#!/usr/bin/env python3
"""
简化版PDF分析器
使用基本Python库分析PDF文件内容
"""
import re
import json
from pathlib import Path
from datetime import datetime

def analyze_pdf_simple(pdf_path):
    """使用简单方法分析PDF文件"""
    print(f"正在分析PDF文件: {pdf_path}")
    
    if not Path(pdf_path).exists():
        print(f"错误: PDF文件不存在: {pdf_path}")
        return None
    
    try:
        # 读取PDF文件的原始内容
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        # 转换为文本（简单方法）
        text = content.decode('latin-1', errors='ignore')
        
        # 基本信息
        file_size = Path(pdf_path).stat().st_size
        
        # 分析结果
        analysis = {
            "file_path": str(pdf_path),
            "file_name": Path(pdf_path).name,
            "file_size": file_size,
            "analysis_time": datetime.now().isoformat(),
            "content_length": len(text)
        }
        
        # 检测PDF版本
        pdf_version_match = re.search(r'%PDF-(\d+\.\d+)', text)
        if pdf_version_match:
            analysis["pdf_version"] = pdf_version_match.group(1)
        
        # 检测语言
        if 'zh-CN' in text or '中文' in text:
            analysis["language"] = "中文"
        elif 'en-US' in text or 'English' in text:
            analysis["language"] = "英文"
        else:
            analysis["language"] = "未知"
        
        # 查找关键词
        keywords = {
            "data_link": ["数据链", "消息", "模拟", "客户端", "开发", "测试"],
            "technical": ["MIL-STD", "6016", "Link16", "J消息", "位段", "字段"],
            "document": ["文档", "报告", "说明", "指南", "手册"],
            "system": ["系统", "架构", "设计", "实现", "功能"]
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
        j_patterns = re.findall(r'J\d+(?:\.\d+)?', text, re.IGNORECASE)
        if j_patterns:
            analysis["j_messages"] = list(set(j_patterns))
        
        # 查找表格相关关键词
        table_keywords = ['word', 'bit', 'field', 'description', 'start', 'end', 'resolution', 'units']
        found_table_keywords = [kw for kw in table_keywords if kw.lower() in text_lower]
        if found_table_keywords:
            analysis["table_keywords"] = found_table_keywords
        
        # 查找位段模式
        bit_patterns = re.findall(r'\d+\s*[-–~\.]{1,2}\s*\d+', text)
        if bit_patterns:
            analysis["bit_patterns"] = bit_patterns[:10]  # 只取前10个
        
        # 查找单位
        units = re.findall(r'\b(deg|rad|ft|m|kts|m/s|km|nm|sec|min|hour)\b', text, re.IGNORECASE)
        if units:
            analysis["units"] = list(set(units))
        
        # 查找DFI/DUI/DI
        dfi_patterns = re.findall(r'DFI\s*\d+', text, re.IGNORECASE)
        dui_patterns = re.findall(r'DUI\s*\d+', text, re.IGNORECASE)
        di_patterns = re.findall(r'DI\s*[:：]', text, re.IGNORECASE)
        
        if dfi_patterns:
            analysis["dfi_patterns"] = dfi_patterns[:5]
        if dui_patterns:
            analysis["dui_patterns"] = dui_patterns[:5]
        if di_patterns:
            analysis["di_patterns"] = di_patterns[:5]
        
        # 提取可读文本预览
        readable_chars = []
        for char in text:
            if char.isprintable() and ord(char) < 128:
                readable_chars.append(char)
            elif char in ['\n', '\r', '\t']:
                readable_chars.append(char)
        
        readable_text = ''.join(readable_chars)
        
        # 查找中文内容
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
        if chinese_chars:
            analysis["chinese_content"] = chinese_chars[:10]  # 前10个中文片段
        
        # 文本预览
        preview_length = 1000
        analysis["text_preview"] = readable_text[:preview_length]
        if len(readable_text) > preview_length:
            analysis["text_preview"] += "..."
        
        return analysis
        
    except Exception as e:
        print(f"分析PDF时出错: {e}")
        return None

def main():
    """主函数"""
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    
    print("=" * 80)
    print("PDF文件内容分析")
    print("=" * 80)
    print(f"目标文件: {Path(pdf_path).name}")
    print(f"文件路径: {pdf_path}")
    
    # 分析PDF内容
    analysis = analyze_pdf_simple(pdf_path)
    
    if analysis:
        print(f"\n✓ 文件大小: {analysis['file_size']:,} bytes")
        print(f"✓ 内容长度: {analysis['content_length']:,} 字符")
        
        if 'pdf_version' in analysis:
            print(f"✓ PDF版本: {analysis['pdf_version']}")
        
        if 'language' in analysis:
            print(f"✓ 语言: {analysis['language']}")
        
        print(f"\n关键词分析:")
        for category, words in analysis['keywords'].items():
            print(f"  {category}: {', '.join(words)}")
        
        if 'j_messages' in analysis:
            print(f"\nJ消息模式: {', '.join(analysis['j_messages'])}")
        
        if 'table_keywords' in analysis:
            print(f"表格关键词: {', '.join(analysis['table_keywords'])}")
        
        if 'bit_patterns' in analysis:
            print(f"位段模式: {', '.join(analysis['bit_patterns'])}")
        
        if 'units' in analysis:
            print(f"单位: {', '.join(analysis['units'])}")
        
        if 'dfi_patterns' in analysis:
            print(f"DFI模式: {', '.join(analysis['dfi_patterns'])}")
        
        if 'dui_patterns' in analysis:
            print(f"DUI模式: {', '.join(analysis['dui_patterns'])}")
        
        if 'di_patterns' in analysis:
            print(f"DI模式: {', '.join(analysis['di_patterns'])}")
        
        if 'chinese_content' in analysis:
            print(f"\n中文内容片段:")
            for i, content in enumerate(analysis['chinese_content'][:5], 1):
                print(f"  {i}. {content}")
        
        print(f"\n文本预览:")
        print(f"  {analysis['text_preview']}")
        
        # 保存分析结果
        output_dir = Path("pdf_analysis_output")
        output_dir.mkdir(exist_ok=True)
        
        analysis_file = output_dir / "pdf_analysis_simple.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 分析结果已保存到: {analysis_file}")
        
        # 生成简要报告
        report_file = output_dir / "analysis_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PDF文件分析报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"文件名: {analysis['file_name']}\n")
            f.write(f"文件大小: {analysis['file_size']:,} bytes\n")
            f.write(f"分析时间: {analysis['analysis_time']}\n\n")
            
            if 'pdf_version' in analysis:
                f.write(f"PDF版本: {analysis['pdf_version']}\n")
            
            if 'language' in analysis:
                f.write(f"语言: {analysis['language']}\n")
            
            f.write(f"\n关键词分析:\n")
            for category, words in analysis['keywords'].items():
                f.write(f"  {category}: {', '.join(words)}\n")
            
            if 'j_messages' in analysis:
                f.write(f"\nJ消息模式: {', '.join(analysis['j_messages'])}\n")
            
            if 'chinese_content' in analysis:
                f.write(f"\n中文内容片段:\n")
                for i, content in enumerate(analysis['chinese_content'][:5], 1):
                    f.write(f"  {i}. {content}\n")
        
        print(f"✓ 简要报告已保存到: {report_file}")
        
        print(f"\n" + "=" * 80)
        print("分析完成!")
        print("=" * 80)
        print("生成的文件:")
        for file in output_dir.glob("*"):
            print(f"  - {file.name} ({file.stat().st_size:,} bytes)")
    
    else:
        print("✗ 分析失败")

if __name__ == "__main__":
    main()

