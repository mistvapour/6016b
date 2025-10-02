#!/usr/bin/env python3
"""
PDF处理功能测试脚本
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_adapter.pdf_processor import PDFProcessor, process_pdf_file

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pdf_processing():
    """测试PDF处理功能"""
    
    # 创建测试输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # 测试PDF文件路径（需要用户提供）
    test_pdf_path = input("请输入测试PDF文件路径: ").strip()
    
    if not test_pdf_path or not Path(test_pdf_path).exists():
        logger.error("PDF文件不存在，请提供有效的PDF文件路径")
        return False
    
    try:
        logger.info(f"开始处理PDF文件: {test_pdf_path}")
        
        # 处理PDF文件
        result = process_pdf_file(
            pdf_path=test_pdf_path,
            output_dir=str(output_dir),
            standard="MIL-STD-6016",
            edition="B"
        )
        
        if result['success']:
            logger.info("PDF处理成功!")
            logger.info(f"输出目录: {result['output_dir']}")
            logger.info(f"生成文件: {result['yaml_files']}")
            
            # 显示处理统计
            if 'sim' in result:
                sim = result['sim']
                logger.info(f"J消息数量: {len(sim.get('j_messages', []))}")
                logger.info(f"DFI/DUI/DI数量: {len(sim.get('dfi_dui_di', []))}")
                logger.info(f"枚举数量: {len(sim.get('enums', []))}")
                logger.info(f"单位数量: {len(sim.get('units', []))}")
            
            # 显示校验结果
            if 'validation_result' in result:
                validation = result['validation_result']
                logger.info(f"校验状态: {'通过' if validation['valid'] else '失败'}")
                logger.info(f"覆盖率: {validation['coverage']:.2%}")
                logger.info(f"置信度: {validation['confidence']:.2%}")
                logger.info(f"错误数量: {len(validation['errors'])}")
                logger.info(f"警告数量: {len(validation['warnings'])}")
            
            return True
        else:
            logger.error(f"PDF处理失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        return False

def test_components():
    """测试各个组件功能"""
    logger.info("测试PDF处理组件...")
    
    try:
        # 测试表格提取器
        from pdf_adapter.extract_tables import TableExtractor
        extractor = TableExtractor()
        logger.info("✓ 表格提取器初始化成功")
        
        # 测试章节解析器
        from pdf_adapter.parse_sections import SectionParser
        parser = SectionParser()
        logger.info("✓ 章节解析器初始化成功")
        
        # 测试字段标准化器
        from pdf_adapter.normalize_bits import FieldNormalizer
        normalizer = FieldNormalizer()
        logger.info("✓ 字段标准化器初始化成功")
        
        # 测试SIM构建器
        from pdf_adapter.build_sim import SIMBuilder
        builder = SIMBuilder()
        logger.info("✓ SIM构建器初始化成功")
        
        # 测试校验器
        from pdf_adapter.validators import ComprehensiveValidator
        validator = ComprehensiveValidator()
        logger.info("✓ 校验器初始化成功")
        
        logger.info("所有组件测试通过!")
        return True
        
    except Exception as e:
        logger.error(f"组件测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("PDF处理系统测试")
    print("=" * 60)
    
    # 测试组件
    if not test_components():
        print("组件测试失败，请检查依赖安装")
        return
    
    print("\n组件测试通过，开始PDF处理测试...")
    
    # 测试PDF处理
    if test_pdf_processing():
        print("\n✓ PDF处理测试完成!")
    else:
        print("\n✗ PDF处理测试失败!")

if __name__ == "__main__":
    main()
