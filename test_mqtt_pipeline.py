#!/usr/bin/env python3
"""
MQTT PDF处理流水线测试脚本
测试从PDF到YAML再到数据库的完整流程
"""
import os
import sys
import requests
import json
import time
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API配置
API_BASE = "http://localhost:8000"
MQTT_API_BASE = "http://localhost:8000/api/mqtt"

def test_mqtt_health():
    """测试MQTT模块健康状态"""
    logger.info("🔍 测试MQTT模块健康状态...")
    try:
        response = requests.get(f"{MQTT_API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                logger.info("✅ MQTT模块健康检查通过")
                logger.info(f"   依赖: {data.get('dependencies', {})}")
                return True
            else:
                logger.error(f"❌ MQTT模块不健康: {data.get('error')}")
                return False
        else:
            logger.error(f"❌ MQTT健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ MQTT健康检查异常: {e}")
        return False

def create_sample_mqtt_pdf():
    """创建示例MQTT PDF文件（模拟）"""
    logger.info("📄 创建示例MQTT PDF文件...")
    
    # 检查是否已有PDF文件
    test_pdfs = [
        "mqtt-v5.0-import.pdf",
        "docs/mqtt-v5.0-import.pdf", 
        "sample_mqtt.pdf"
    ]
    
    for pdf_path in test_pdfs:
        if Path(pdf_path).exists():
            logger.info(f"✅ 找到测试PDF文件: {pdf_path}")
            return pdf_path
    
    # 如果没有找到，使用现有的sample_j_message.pdf作为测试
    if Path("sample_j_message.pdf").exists():
        logger.info("⚠️  使用sample_j_message.pdf作为测试文件（非MQTT格式）")
        return "sample_j_message.pdf"
    
    logger.error("❌ 未找到测试PDF文件")
    return None

def test_pdf_to_yaml(pdf_path):
    """测试PDF到YAML转换"""
    logger.info("🔄 测试PDF到YAML转换...")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            params = {
                'pages': '10-50',  # 较小的页面范围用于测试
                'output_dir': 'test_mqtt_output'
            }
            
            response = requests.post(
                f"{MQTT_API_BASE}/pdf_to_yaml",
                files=files,
                params=params,
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info("✅ PDF到YAML转换成功")
                data = result.get("data", {})
                logger.info(f"   处理页面: {data.get('pages_processed', 0)}")
                logger.info(f"   发现章节: {data.get('sections_found', 0)}")
                logger.info(f"   提取表格: {data.get('tables_extracted', 0)}")
                logger.info(f"   创建消息: {data.get('messages_created', 0)}")
                logger.info(f"   总字段数: {data.get('total_fields', 0)}")
                logger.info(f"   输出目录: {data.get('output_dir')}")
                
                # 显示章节信息
                for section in data.get('sections', []):
                    logger.info(f"   章节: {section['label']} (页面: {section['pages']})")
                
                return result
            else:
                logger.error(f"❌ PDF转换失败: {result.get('message')}")
                return None
        else:
            logger.error(f"❌ PDF转换请求失败: HTTP {response.status_code}")
            logger.error(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ PDF转换异常: {e}")
        return None

def test_yaml_validation(yaml_path):
    """测试YAML文件验证"""
    logger.info("🔍 测试YAML文件验证...")
    
    try:
        response = requests.post(
            f"{MQTT_API_BASE}/validate_yaml",
            params={'yaml_path': yaml_path},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            validation = result.get('validation', {})
            
            if validation.get('valid'):
                logger.info("✅ YAML验证通过")
                logger.info(f"   消息数量: {validation.get('message_count', 0)}")
                logger.info(f"   枚举数量: {validation.get('enum_count', 0)}")
                return True
            else:
                logger.warning("⚠️  YAML验证发现问题:")
                for issue in validation.get('issues', []):
                    logger.warning(f"   - {issue}")
                return False
        else:
            logger.error(f"❌ YAML验证请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ YAML验证异常: {e}")
        return False

def test_database_import(yaml_path, dry_run=True):
    """测试数据库导入"""
    action = "试运行" if dry_run else "实际"
    logger.info(f"🗄️  测试数据库导入（{action}）...")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/import/yaml",
            params={
                'yaml_path': yaml_path,
                'dry_run': dry_run
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info(f"✅ 数据库导入{action}成功")
                stats = result.get('stats', {})
                logger.info(f"   J消息: {stats.get('j_messages', 0)}")
                logger.info(f"   字段: {stats.get('fields', 0)}")
                logger.info(f"   枚举: {stats.get('enums', 0)}")
                logger.info(f"   单位: {stats.get('units', 0)}")
                
                if result.get('stats', {}).get('errors'):
                    logger.warning("   发现错误:")
                    for error in result['stats']['errors'][:3]:
                        logger.warning(f"     - {error}")
                
                return True
            else:
                logger.error(f"❌ 数据库导入{action}失败: {result.get('error')}")
                return False
        else:
            logger.error(f"❌ 数据库导入请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库导入异常: {e}")
        return False

def test_complete_pipeline(pdf_path):
    """测试完整流水线"""
    logger.info("🚀 测试完整流水线（PDF→YAML→数据库）...")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            params = {
                'pages': '10-30',  # 更小的范围用于快速测试
                'output_dir': 'test_pipeline_output',
                'import_to_db': True,
                'dry_run': True
            }
            
            response = requests.post(
                f"{MQTT_API_BASE}/complete_pipeline",
                files=files,
                params=params,
                timeout=180
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info("✅ 完整流水线执行成功")
                
                # PDF处理结果
                pdf_result = result.get('pdf_processing', {})
                if pdf_result.get('success'):
                    data = pdf_result.get('data', {})
                    logger.info(f"   PDF处理: 成功 ({data.get('messages_created', 0)} 消息)")
                
                # 数据库导入结果
                db_result = result.get('database_import')
                if db_result:
                    if db_result.get('success'):
                        logger.info("   数据库导入: 成功（试运行）")
                    else:
                        logger.warning(f"   数据库导入: 失败 - {db_result.get('error')}")
                
                return True
            else:
                logger.error(f"❌ 完整流水线失败: {result.get('message')}")
                return False
        else:
            logger.error(f"❌ 完整流水线请求失败: HTTP {response.status_code}")
            logger.error(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 完整流水线异常: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    logger.info("📁 测试文件操作...")
    
    try:
        # 测试列出输出文件
        response = requests.get(
            f"{MQTT_API_BASE}/list_outputs",
            params={'output_dir': 'test_mqtt_output'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            files = result.get('files', [])
            logger.info(f"✅ 文件列表获取成功: {len(files)} 个文件")
            
            for file in files[:3]:  # 显示前3个文件
                logger.info(f"   - {file['name']} ({file['size']} bytes)")
            
            return True
        else:
            logger.error(f"❌ 文件列表获取失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 文件操作异常: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    logger.info("=" * 60)
    logger.info("MQTT PDF处理流水线测试")
    logger.info("=" * 60)
    
    # 检查服务状态
    logger.info("检查API服务状态...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code != 200:
            logger.error("❌ 主API服务不可用，请先启动服务")
            return False
    except:
        logger.error("❌ 无法连接到API服务，请检查服务是否启动")
        return False
    
    tests = [
        ("MQTT模块健康检查", test_mqtt_health),
        ("文件操作", test_file_operations),
    ]
    
    # 准备测试PDF
    pdf_path = create_sample_mqtt_pdf()
    if pdf_path:
        tests.extend([
            ("PDF到YAML转换", lambda: test_pdf_to_yaml(pdf_path)),
            ("完整流水线", lambda: test_complete_pipeline(pdf_path))
        ])
    else:
        logger.warning("⚠️  跳过PDF相关测试，因为没有找到测试文件")
    
    # 执行测试
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # 避免请求过快
    
    # 输出测试结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    logger.info(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！MQTT流水线运行正常。")
        return True
    else:
        logger.info("⚠️  部分测试失败，请检查配置。")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        pdf_path = create_sample_mqtt_pdf()
        
        if test_name == "health":
            test_mqtt_health()
        elif test_name == "pdf" and pdf_path:
            test_pdf_to_yaml(pdf_path)
        elif test_name == "pipeline" and pdf_path:
            test_complete_pipeline(pdf_path)
        elif test_name == "files":
            test_file_operations()
        else:
            logger.error("未知测试名称或缺少PDF文件")
            logger.info("可用选项: health, pdf, pipeline, files")
    else:
        run_all_tests()

if __name__ == "__main__":
    main()
