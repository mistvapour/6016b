#!/usr/bin/env python3
"""
使用样例PDF文件测试PDF处理系统
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sample_pdf():
    """测试样例PDF文件"""
    
    # 样例PDF文件路径
    sample_pdf_path = "sample_j_message.pdf"
    
    if not Path(sample_pdf_path).exists():
        logger.error(f"样例PDF文件不存在: {sample_pdf_path}")
        return False
    
    try:
        # 导入PDF处理模块
        from backend.pdf_adapter.pdf_processor import PDFProcessor
        
        # 创建输出目录
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"开始处理样例PDF文件: {sample_pdf_path}")
        
        # 创建PDF处理器
        processor = PDFProcessor(standard="MIL-STD-6016", edition="B")
        
        # 处理PDF文件
        result = processor.process_pdf(sample_pdf_path, str(output_dir))
        
        if result['success']:
            logger.info("✓ PDF处理成功!")
            
            # 显示处理结果
            logger.info(f"输出目录: {result['output_dir']}")
            logger.info(f"生成文件: {result['yaml_files']}")
            
            # 显示SIM统计
            if 'sim' in result:
                sim = result['sim']
                logger.info(f"J消息数量: {len(sim.get('j_messages', []))}")
                logger.info(f"DFI/DUI/DI数量: {len(sim.get('dfi_dui_di', []))}")
                logger.info(f"枚举数量: {len(sim.get('enums', []))}")
                logger.info(f"单位数量: {len(sim.get('units', []))}")
                
                # 显示J消息详情
                for i, message in enumerate(sim.get('j_messages', [])):
                    logger.info(f"J消息 {i+1}: {message.get('label', 'N/A')} - {message.get('title', 'N/A')}")
                    for j, word in enumerate(message.get('words', [])):
                        logger.info(f"  字 {j+1}: {len(word.get('fields', []))} 个字段")
                        for k, field in enumerate(word.get('fields', [])):
                            logger.info(f"    字段 {k+1}: {field.get('name', 'N/A')} (位段: {field.get('bits', 'N/A')})")
            
            # 显示校验结果
            if 'validation_result' in result:
                validation = result['validation_result']
                logger.info(f"校验状态: {'通过' if validation['valid'] else '失败'}")
                logger.info(f"覆盖率: {validation['coverage']:.2%}")
                logger.info(f"置信度: {validation['confidence']:.2%}")
                logger.info(f"错误数量: {len(validation['errors'])}")
                logger.info(f"警告数量: {len(validation['warnings'])}")
                
                # 显示错误详情
                if validation['errors']:
                    logger.info("错误详情:")
                    for error in validation['errors']:
                        logger.info(f"  - {error.get('message', 'N/A')}")
                
                # 显示警告详情
                if validation['warnings']:
                    logger.info("警告详情:")
                    for warning in validation['warnings']:
                        logger.info(f"  - {warning.get('message', 'N/A')}")
            
            # 显示生成的文件
            if result['yaml_files']:
                logger.info("生成的YAML文件:")
                for filename in result['yaml_files']:
                    file_path = output_dir / filename
                    if file_path.exists():
                        logger.info(f"  - {filename} ({file_path.stat().st_size} bytes)")
                        # 显示文件内容预览
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            logger.info(f"    预览 (前5行):")
                            for line in lines[:5]:
                                logger.info(f"      {line}")
                            if len(lines) > 5:
                                logger.info(f"      ... (共{len(lines)}行)")
            
            return True
        else:
            logger.error(f"✗ PDF处理失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """测试各个组件"""
    logger.info("测试PDF处理组件...")
    
    try:
        # 测试表格提取
        from backend.pdf_adapter.extract_tables import extract_tables_from_pdf
        logger.info("测试表格提取...")
        tables = extract_tables_from_pdf("sample_j_message.pdf")
        logger.info(f"提取到 {len(tables)} 页的表格数据")
        
        # 测试章节解析
        from backend.pdf_adapter.parse_sections import parse_6016_sections
        logger.info("测试章节解析...")
        sections = parse_6016_sections("sample_j_message.pdf")
        logger.info(f"解析到 {len(sections.get('j_messages', []))} 个J消息")
        logger.info(f"解析到 {len(sections.get('appendix_b', []))} 个Appendix B章节")
        
        # 测试数据标准化
        from backend.pdf_adapter.normalize_bits import normalize_pdf_data, validate_extracted_data
        logger.info("测试数据标准化...")
        
        # 模拟一些字段数据进行测试
        sample_fields = [
            {
                'field_name': 'Test Field 1',
                'bit': '0-5',
                'description': 'Test description with units deg'
            },
            {
                'field_name': 'Test Field 2', 
                'bit': '6-15',
                'description': 'Another test field'
            }
        ]
        
        normalized = normalize_pdf_data(sample_fields)
        logger.info(f"标准化了 {len(normalized)} 个字段")
        
        validation = validate_extracted_data(normalized)
        logger.info(f"校验结果: 有效={validation['valid']}, 覆盖率={validation['coverage']:.2%}")
        
        logger.info("✓ 所有组件测试通过")
        return True
        
    except Exception as e:
        logger.error(f"组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("PDF处理系统 - 样例文件测试")
    print("=" * 60)
    
    # 检查样例文件
    if not Path("sample_j_message.pdf").exists():
        print("✗ 样例PDF文件不存在: sample_j_message.pdf")
        print("请确保文件在当前目录下")
        return
    
    # 测试各个组件
    print("\n1. 测试各个组件...")
    if not test_individual_components():
        print("组件测试失败，请检查依赖安装")
        return
    
    print("\n2. 测试完整PDF处理流程...")
    if test_sample_pdf():
        print("\n✓ 样例PDF处理测试完成!")
        print("\n可以查看 test_output/ 目录下的生成文件")
    else:
        print("\n✗ 样例PDF处理测试失败!")

if __name__ == "__main__":
    main()
