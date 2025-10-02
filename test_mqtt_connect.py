#!/usr/bin/env python3
"""
使用具体的MQTT CONNECT测试PDF测试流水线
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
import subprocess

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试文件路径
TEST_PDF = "test_sample/mqtt_connect_test.pdf"
OUTPUT_DIR = "mqtt_connect_output"

def check_pdf_file():
    """检查测试PDF文件"""
    logger.info("🔍 检查测试PDF文件...")
    
    if not Path(TEST_PDF).exists():
        logger.error(f"❌ 测试PDF文件不存在: {TEST_PDF}")
        return False
    
    file_size = Path(TEST_PDF).stat().st_size
    logger.info(f"✅ 找到测试PDF文件: {TEST_PDF} ({file_size} bytes)")
    return True

def start_api_server():
    """启动API服务器（如果未运行）"""
    logger.info("🚀 检查API服务状态...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ API服务已运行")
            return True
    except:
        pass
    
    logger.info("⚠️  API服务未运行，尝试启动...")
    try:
        # 尝试启动服务器
        cmd = "uvicorn backend.main:app --host 0.0.0.0 --port 8000 &"
        subprocess.Popen(cmd, shell=True)
        logger.info("🔄 正在启动API服务，请等待...")
        time.sleep(10)  # 等待服务启动
        
        # 再次检查
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ API服务启动成功")
            return True
        else:
            logger.error("❌ API服务启动失败")
            return False
    except Exception as e:
        logger.error(f"❌ 启动API服务失败: {e}")
        return False

def test_mqtt_health():
    """测试MQTT模块健康状态"""
    logger.info("🔍 测试MQTT模块健康状态...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/api/mqtt/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ MQTT模块健康检查通过")
            logger.info(f"   状态: {data.get('status')}")
            dependencies = data.get('dependencies', {})
            for dep, status in dependencies.items():
                status_text = "✅" if status else "❌"
                logger.info(f"   {dep}: {status_text}")
            return True
        else:
            logger.error(f"❌ MQTT模块健康检查失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ MQTT模块健康检查异常: {e}")
        return False

def test_pdf_to_yaml():
    """测试PDF到YAML转换"""
    logger.info("📄 测试MQTT CONNECT PDF到YAML转换...")
    
    try:
        import requests
        
        with open(TEST_PDF, 'rb') as f:
            files = {'file': (Path(TEST_PDF).name, f, 'application/pdf')}
            params = {
                'pages': '1-10',  # MQTT CONNECT测试可能页面较少
                'output_dir': OUTPUT_DIR
            }
            
            logger.info(f"📤 上传文件: {TEST_PDF}")
            logger.info(f"📄 页面范围: {params['pages']}")
            logger.info(f"📁 输出目录: {params['output_dir']}")
            
            response = requests.post(
                "http://localhost:8000/api/mqtt/pdf_to_yaml",
                files=files,
                params=params,
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                logger.info("✅ PDF到YAML转换成功！")
                
                data = result.get("data", {})
                logger.info("📊 处理统计:")
                logger.info(f"   📄 PDF文件: {data.get('pdf_filename')}")
                logger.info(f"   📃 处理页面: {data.get('pages_processed', 0)}")
                logger.info(f"   📋 发现章节: {data.get('sections_found', 0)}")
                logger.info(f"   📊 提取表格: {data.get('tables_extracted', 0)}")
                logger.info(f"   💬 创建消息: {data.get('messages_created', 0)}")
                logger.info(f"   🔧 总字段数: {data.get('total_fields', 0)}")
                logger.info(f"   📁 输出目录: {data.get('output_dir')}")
                
                # 显示发现的章节
                sections = data.get('sections', [])
                if sections:
                    logger.info("📋 发现的MQTT章节:")
                    for section in sections:
                        pages_str = ', '.join(map(str, section['pages']))
                        logger.info(f"   🔸 {section['label']} (页面: {pages_str})")
                        subsections = section.get('subsections', [])
                        if subsections:
                            logger.info(f"     子章节: {', '.join(subsections)}")
                
                # 显示生成的文件
                files_generated = data.get('files', [])
                if files_generated:
                    logger.info("📁 生成的文件:")
                    for file_path in files_generated[:5]:  # 显示前5个文件
                        logger.info(f"   📄 {file_path}")
                    if len(files_generated) > 5:
                        logger.info(f"   ... 还有 {len(files_generated) - 5} 个文件")
                
                # 显示校验结果
                validation = data.get('validation', {})
                sim_issues = validation.get('sim_issues', [])
                yaml_validation = validation.get('yaml_validation', {})
                
                if sim_issues:
                    logger.warning("⚠️  SIM校验发现问题:")
                    for issue in sim_issues[:3]:
                        logger.warning(f"   - {issue}")
                
                if yaml_validation.get('valid'):
                    logger.info("✅ YAML格式验证通过")
                    logger.info(f"   📧 消息数量: {yaml_validation.get('message_count', 0)}")
                    logger.info(f"   🏷️  枚举数量: {yaml_validation.get('enum_count', 0)}")
                else:
                    logger.warning("⚠️  YAML格式验证发现问题:")
                    for issue in yaml_validation.get('issues', [])[:3]:
                        logger.warning(f"   - {issue}")
                
                return result
                
            else:
                logger.error(f"❌ PDF转换失败: {result.get('message')}")
                return None
        else:
            logger.error(f"❌ PDF转换请求失败: HTTP {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"   错误详情: {error_data.get('detail', response.text)}")
            except:
                logger.error(f"   响应内容: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ PDF转换异常: {e}")
        return None

def test_yaml_validation(yaml_path):
    """测试生成的YAML文件验证"""
    logger.info("🔍 测试YAML文件验证...")
    
    if not Path(yaml_path).exists():
        logger.error(f"❌ YAML文件不存在: {yaml_path}")
        return False
    
    try:
        import requests
        
        response = requests.post(
            "http://localhost:8000/api/mqtt/validate_yaml",
            params={'yaml_path': yaml_path},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            validation = result.get('validation', {})
            
            if validation.get('valid'):
                logger.info("✅ YAML文件验证通过")
                logger.info(f"   📧 消息数量: {validation.get('message_count', 0)}")
                logger.info(f"   🏷️  枚举数量: {validation.get('enum_count', 0)}")
                return True
            else:
                logger.warning("⚠️  YAML文件验证发现问题:")
                for issue in validation.get('issues', []):
                    logger.warning(f"   - {issue}")
                return False
        else:
            logger.error(f"❌ YAML验证请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ YAML验证异常: {e}")
        return False

def test_database_import(yaml_path):
    """测试数据库导入（试运行）"""
    logger.info("🗄️  测试数据库导入（试运行）...")
    
    try:
        import requests
        
        response = requests.post(
            "http://localhost:8000/api/import/yaml",
            params={
                'yaml_path': yaml_path,
                'dry_run': True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                logger.info("✅ 数据库导入试运行成功")
                
                stats = result.get('stats', {})
                logger.info("📊 导入统计:")
                logger.info(f"   📧 J消息: {stats.get('j_messages', 0)}")
                logger.info(f"   🔧 字段: {stats.get('fields', 0)}")
                logger.info(f"   🏷️  枚举: {stats.get('enums', 0)}")
                logger.info(f"   📏 单位: {stats.get('units', 0)}")
                
                errors = stats.get('errors', [])
                if errors:
                    logger.warning("⚠️  发现错误:")
                    for error in errors[:3]:
                        logger.warning(f"   - {error}")
                
                return True
            else:
                logger.error(f"❌ 数据库导入试运行失败: {result.get('error')}")
                return False
        else:
            logger.error(f"❌ 数据库导入请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库导入异常: {e}")
        return False

def test_complete_pipeline():
    """测试完整流水线"""
    logger.info("🚀 测试完整流水线（PDF→YAML→数据库）...")
    
    try:
        import requests
        
        with open(TEST_PDF, 'rb') as f:
            files = {'file': (Path(TEST_PDF).name, f, 'application/pdf')}
            params = {
                'pages': '1-10',
                'output_dir': f'{OUTPUT_DIR}_pipeline',
                'import_to_db': True,
                'dry_run': True
            }
            
            logger.info("🔄 执行完整流水线...")
            
            response = requests.post(
                "http://localhost:8000/api/mqtt/complete_pipeline",
                files=files,
                params=params,
                timeout=180
            )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                logger.info("✅ 完整流水线执行成功！")
                
                # PDF处理结果
                pdf_result = result.get('pdf_processing', {})
                if pdf_result.get('success'):
                    data = pdf_result.get('data', {})
                    logger.info(f"   📄 PDF处理: 成功 ({data.get('messages_created', 0)} 消息)")
                else:
                    logger.warning(f"   📄 PDF处理: 失败 - {pdf_result.get('message')}")
                
                # 数据库导入结果
                db_result = result.get('database_import')
                if db_result:
                    if db_result.get('success'):
                        logger.info("   🗄️  数据库导入: 成功（试运行）")
                        stats = db_result.get('stats', {})
                        logger.info(f"     📧 导入消息: {stats.get('j_messages', 0)}")
                        logger.info(f"     🔧 导入字段: {stats.get('fields', 0)}")
                    else:
                        logger.warning(f"   🗄️  数据库导入: 失败 - {db_result.get('error')}")
                else:
                    logger.info("   🗄️  数据库导入: 未执行")
                
                return True
            else:
                logger.error(f"❌ 完整流水线失败: {result.get('message')}")
                return False
        else:
            logger.error(f"❌ 完整流水线请求失败: HTTP {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"   错误详情: {error_data.get('detail', response.text)}")
            except:
                logger.error(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 完整流水线异常: {e}")
        return False

def examine_output_files():
    """检查输出文件"""
    logger.info("📁 检查生成的输出文件...")
    
    output_path = Path(OUTPUT_DIR)
    if not output_path.exists():
        logger.warning("⚠️  输出目录不存在")
        return
    
    files = list(output_path.rglob("*"))
    files = [f for f in files if f.is_file()]
    
    if not files:
        logger.warning("⚠️  输出目录为空")
        return
    
    logger.info(f"📁 找到 {len(files)} 个输出文件:")
    
    for file in files:
        relative_path = file.relative_to(output_path)
        file_size = file.stat().st_size
        logger.info(f"   📄 {relative_path} ({file_size} bytes)")
    
    # 显示主要文件内容摘要
    main_yaml = output_path / "mqtt_v5_complete.yaml"
    if main_yaml.exists():
        logger.info("\n📄 主YAML文件内容摘要:")
        try:
            with open(main_yaml, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10]):
                    logger.info(f"   {i+1:2d}: {line.rstrip()}")
                if len(lines) > 10:
                    logger.info(f"   ... 还有 {len(lines) - 10} 行")
        except Exception as e:
            logger.error(f"   读取文件失败: {e}")

def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("MQTT CONNECT PDF处理流水线测试")
    logger.info("=" * 60)
    logger.info(f"📄 测试文件: {TEST_PDF}")
    logger.info(f"📁 输出目录: {OUTPUT_DIR}")
    
    # 测试步骤
    tests = [
        ("检查PDF文件", check_pdf_file),
        ("启动API服务", start_api_server),
        ("MQTT模块健康检查", test_mqtt_health),
        ("PDF到YAML转换", test_pdf_to_yaml),
        ("完整流水线测试", test_complete_pipeline),
        ("检查输出文件", examine_output_files),
    ]
    
    results = []
    yaml_path = None
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_name == "PDF到YAML转换":
                result = test_func()
                if result and result.get("success"):
                    yaml_path = result.get("data", {}).get("main_yaml")
                results.append((test_name, result is not None))
            else:
                result = test_func()
                results.append((test_name, result))
                
        except Exception as e:
            logger.error(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
        
        time.sleep(1)
    
    # 如果有YAML文件，测试验证和导入
    if yaml_path and Path(yaml_path).exists():
        logger.info(f"\n🧪 YAML文件验证")
        logger.info("-" * 40)
        yaml_valid = test_yaml_validation(yaml_path)
        results.append(("YAML文件验证", yaml_valid))
        
        logger.info(f"\n🧪 数据库导入测试")
        logger.info("-" * 40)
        db_import = test_database_import(yaml_path)
        results.append(("数据库导入测试", db_import))
    
    # 输出测试结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    logger.info(f"\n📊 总计: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！MQTT CONNECT PDF处理成功。")
        logger.info(f"📁 查看输出文件: {OUTPUT_DIR}/")
        return True
    else:
        logger.info("⚠️  部分测试失败，请检查日志了解详情。")
        return False

if __name__ == "__main__":
    main()
