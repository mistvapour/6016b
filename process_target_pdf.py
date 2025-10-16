#!/usr/bin/env python3
"""
处理指定的PDF文件：公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf
"""
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from pdf_adapter.pdf_processor import PDFProcessor
    from universal_import_system import UniversalImportSystem
    import fitz  # PyMuPDF
    import json
    import yaml
    from datetime import datetime
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装必要的依赖包")
    sys.exit(1)

def analyze_pdf_content(pdf_path):
    """分析PDF文件内容"""
    print(f"正在分析PDF文件: {pdf_path}")
    
    if not Path(pdf_path).exists():
        print(f"错误: PDF文件不存在: {pdf_path}")
        return None
    
    try:
        # 使用PyMuPDF打开PDF
        doc = fitz.open(pdf_path)
        print(f"PDF页数: {len(doc)}")
        
        # 提取前几页的文本进行分析
        text_sample = ""
        for page_num in range(min(5, len(doc))):
            page = doc[page_num]
            text_sample += page.get_text()
        
        doc.close()
        
        # 分析内容
        analysis = {
            "file_path": pdf_path,
            "file_size": Path(pdf_path).stat().st_size,
            "page_count": len(doc),
            "text_length": len(text_sample),
            "analysis_time": datetime.now().isoformat()
        }
        
        # 检测标准类型
        text_lower = text_sample.lower()
        
        if 'mil-std-6016' in text_lower or 'link 16' in text_lower:
            analysis["detected_standard"] = "MIL-STD-6016"
            analysis["confidence"] = 0.95
        elif 'mqtt' in text_lower:
            analysis["detected_standard"] = "MQTT"
            analysis["confidence"] = 0.90
        elif '数据链' in text_sample or '消息' in text_sample:
            analysis["detected_standard"] = "数据链相关"
            analysis["confidence"] = 0.85
        else:
            analysis["detected_standard"] = "未知"
            analysis["confidence"] = 0.50
        
        # 查找关键词
        keywords = {
            "j_message": ["j2.0", "j2.1", "j2.2", "j2.3", "j2.4", "j10.2"],
            "data_link": ["数据链", "消息", "模拟", "客户端"],
            "technical": ["位段", "字段", "编码", "格式"],
            "testing": ["测试", "开发", "验证"]
        }
        
        found_keywords = {}
        for category, words in keywords.items():
            found_keywords[category] = [word for word in words if word.lower() in text_lower]
        
        analysis["keywords"] = found_keywords
        
        # 提取可读文本预览
        readable_text = ''.join(c for c in text_sample if c.isprintable() and ord(c) < 128)
        analysis["text_preview"] = readable_text[:500] + "..." if len(readable_text) > 500 else readable_text
        
        return analysis
        
    except Exception as e:
        print(f"分析PDF时出错: {e}")
        return None

def process_with_universal_system(pdf_path):
    """使用通用导入系统处理PDF"""
    print("\n使用通用导入系统处理PDF...")
    
    try:
        # 创建通用导入系统实例
        import_system = UniversalImportSystem()
        
        # 处理PDF文件
        result = import_system.process_file(pdf_path)
        
        return result
        
    except Exception as e:
        print(f"通用导入系统处理失败: {e}")
        return None

def main():
    """主函数"""
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    
    print("=" * 80)
    print("PDF文件处理分析")
    print("=" * 80)
    print(f"目标文件: {Path(pdf_path).name}")
    print(f"文件路径: {pdf_path}")
    
    # 1. 基础内容分析
    print("\n1. 基础内容分析")
    analysis = analyze_pdf_content(pdf_path)
    
    if analysis:
        print(f"✓ 文件大小: {analysis['file_size']:,} bytes")
        print(f"✓ 页数: {analysis['page_count']}")
        print(f"✓ 检测到的标准: {analysis['detected_standard']} (置信度: {analysis['confidence']:.1%})")
        
        print("\n关键词分析:")
        for category, words in analysis['keywords'].items():
            if words:
                print(f"  {category}: {', '.join(words)}")
        
        print(f"\n文本预览:")
        print(f"  {analysis['text_preview']}")
        
        # 保存分析结果
        output_dir = Path("pdf_analysis_output")
        output_dir.mkdir(exist_ok=True)
        
        analysis_file = output_dir / "pdf_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n✓ 分析结果已保存到: {analysis_file}")
    
    # 2. 使用通用导入系统处理
    print("\n2. 使用通用导入系统处理")
    process_result = process_with_universal_system(pdf_path)
    
    if process_result:
        print("✓ 处理结果:")
        print(f"  成功: {process_result.get('success', False)}")
        if 'standard' in process_result:
            print(f"  标准: {process_result['standard']}")
        if 'messages' in process_result:
            print(f"  消息数量: {len(process_result['messages'])}")
        if 'yaml_path' in process_result:
            print(f"  YAML文件: {process_result['yaml_path']}")
        
        # 保存处理结果
        if output_dir:
            result_file = output_dir / "processing_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(process_result, f, indent=2, ensure_ascii=False)
            print(f"✓ 处理结果已保存到: {result_file}")
    else:
        print("✗ 处理失败")
    
    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)
    
    if output_dir and output_dir.exists():
        print("生成的文件:")
        for file in output_dir.glob("*"):
            print(f"  - {file.name} ({file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()

