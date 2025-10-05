#!/usr/bin/env python3
"""
MQTT PDF处理快速测试
使用curl命令演示完整流水线
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🔄 {description}")
    print(f"命令: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 成功")
            print(result.stdout)
            return True, result.stdout
        else:
            print("❌ 失败")
            print(result.stderr)
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("❌ 超时")
        return False, "Command timeout"
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, str(e)

def main():
    print("=" * 60)
    print("MQTT PDF处理流水线快速测试")
    print("=" * 60)
    
    # 检查服务状态
    print("\n1. 检查服务状态")
    success, _ = run_command(
        'curl -s "http://127.0.0.1:8000/api/health"',
        "检查主API服务"
    )
    
    if not success:
        print("❌ 主API服务不可用，请先启动服务：")
        print("   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    success, _ = run_command(
        'curl -s "http://127.0.0.1:8000/api/mqtt/health"',
        "检查MQTT模块"
    )
    
    if not success:
        print("❌ MQTT模块不可用")
        return
    
    # 查找测试PDF文件
    print("\n2. 查找测试PDF文件")
    pdf_file = None
    test_files = ["sample_j_message.pdf", "mqtt-v5.0-import.pdf", "docs/mqtt-v5.0-import.pdf"]
    
    for file in test_files:
        if Path(file).exists():
            pdf_file = file
            print(f"✅ 找到测试文件: {file}")
            break
    
    if not pdf_file:
        print("❌ 未找到测试PDF文件")
        return
    
    # 测试PDF到YAML转换
    print("\n3. 测试PDF到YAML转换")
    success, output = run_command(
        f'curl -X POST "http://127.0.0.1:8000/api/mqtt/pdf_to_yaml?pages=10-50&output_dir=quick_test_output" '
        f'-F "file=@{pdf_file}" -H "Content-Type: multipart/form-data"',
        "PDF到YAML转换"
    )
    
    if success:
        try:
            result = json.loads(output)
            if result.get("success"):
                data = result.get("data", {})
                print(f"   📊 处理统计:")
                print(f"     - 处理页面: {data.get('pages_processed', 0)}")
                print(f"     - 发现章节: {data.get('sections_found', 0)}")
                print(f"     - 提取表格: {data.get('tables_extracted', 0)}")
                print(f"     - 创建消息: {data.get('messages_created', 0)}")
                print(f"     - 总字段数: {data.get('total_fields', 0)}")
                main_yaml = data.get('main_yaml')
            else:
                print(f"   ❌ 转换失败: {result.get('message')}")
                return
        except json.JSONDecodeError:
            print("   ❌ 响应格式错误")
            return
    else:
        return
    
    # 验证生成的YAML
    if main_yaml and Path(main_yaml).exists():
        print("\n4. 验证生成的YAML文件")
        success, output = run_command(
            f'curl -X POST "http://127.0.0.1:8000/api/mqtt/validate_yaml?yaml_path={main_yaml}"',
            "YAML文件验证"
        )
        
        if success:
            try:
                result = json.loads(output)
                validation = result.get('validation', {})
                if validation.get('valid'):
                    print(f"   ✅ YAML验证通过")
                    print(f"     - 消息数量: {validation.get('message_count', 0)}")
                    print(f"     - 枚举数量: {validation.get('enum_count', 0)}")
                else:
                    print(f"   ⚠️  YAML验证发现问题:")
                    for issue in validation.get('issues', [])[:3]:
                        print(f"     - {issue}")
            except json.JSONDecodeError:
                print("   ❌ 验证响应格式错误")
    
    # 测试数据库导入（试运行）
    if main_yaml and Path(main_yaml).exists():
        print("\n5. 测试数据库导入（试运行）")
        success, output = run_command(
            f'curl -X POST "http://127.0.0.1:8000/api/import/yaml?yaml_path={main_yaml}&dry_run=true"',
            "数据库导入试运行"
        )
        
        if success:
            try:
                result = json.loads(output)
                if result.get("success"):
                    print(f"   ✅ 导入试运行成功")
                    stats = result.get('stats', {})
                    print(f"     - J消息: {stats.get('j_messages', 0)}")
                    print(f"     - 字段: {stats.get('fields', 0)}")
                    print(f"     - 枚举: {stats.get('enums', 0)}")
                else:
                    print(f"   ❌ 导入试运行失败: {result.get('error')}")
            except json.JSONDecodeError:
                print("   ❌ 导入响应格式错误")
    
    # 测试完整流水线
    print("\n6. 测试完整流水线")
    success, output = run_command(
        f'curl -X POST "http://127.0.0.1:8000/api/mqtt/complete_pipeline?pages=10-30&output_dir=pipeline_test_output&import_to_db=true&dry_run=true" '
        f'-F "file=@{pdf_file}" -H "Content-Type: multipart/form-data"',
        "完整流水线测试"
    )
    
    if success:
        try:
            result = json.loads(output)
            if result.get("success"):
                print(f"   ✅ 完整流水线成功")
                
                # PDF处理结果
                pdf_result = result.get('pdf_processing', {})
                if pdf_result.get('success'):
                    data = pdf_result.get('data', {})
                    print(f"     - PDF处理: 成功 ({data.get('messages_created', 0)} 消息)")
                
                # 数据库导入结果
                db_result = result.get('database_import')
                if db_result and db_result.get('success'):
                    print(f"     - 数据库导入: 成功（试运行）")
            else:
                print(f"   ❌ 完整流水线失败: {result.get('message')}")
        except json.JSONDecodeError:
            print("   ❌ 流水线响应格式错误")
    
    # 显示生成的文件
    print("\n7. 查看生成的文件")
    success, output = run_command(
        'curl -s "http://127.0.0.1:8000/api/mqtt/list_outputs?output_dir=quick_test_output"',
        "列出生成的文件"
    )
    
    if success:
        try:
            result = json.loads(output)
            files = result.get('files', [])
            print(f"   📁 生成了 {len(files)} 个文件:")
            for file in files[:5]:  # 显示前5个文件
                print(f"     - {file['name']} ({file['size']} bytes)")
            if len(files) > 5:
                print(f"     ... 还有 {len(files) - 5} 个文件")
        except json.JSONDecodeError:
            print("   ❌ 文件列表响应格式错误")
    
    print("\n" + "=" * 60)
    print("🎉 MQTT PDF处理流水线测试完成！")
    print("=" * 60)
    print("\n📖 使用说明:")
    print("1. PDF→YAML: POST /api/mqtt/pdf_to_yaml")
    print("2. YAML验证: POST /api/mqtt/validate_yaml")  
    print("3. 数据库导入: POST /api/import/yaml")
    print("4. 完整流水线: POST /api/mqtt/complete_pipeline")
    print("\n📁 生成的文件位置:")
    print("- 主YAML: quick_test_output/mqtt_v5_complete.yaml")
    print("- JSON格式: quick_test_output/mqtt_v5_complete.json")
    print("- 单独消息: quick_test_output/messages/")
    print("- 导入清单: quick_test_output/import_manifest.yaml")

if __name__ == "__main__":
    main()
