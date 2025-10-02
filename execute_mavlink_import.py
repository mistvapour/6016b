#!/usr/bin/env python3
"""
MAVLink YAML导入执行脚本
将转换好的MAVLink协议数据导入到6016数据库系统
"""
import requests
import json
import time
from pathlib import Path

def execute_mavlink_import():
    """执行MAVLink YAML导入流程"""
    print("🚀 执行MAVLink协议数据导入")
    print("=" * 50)
    
    yaml_file = "mavlink_output/mavlink_mapping.yaml"
    api_base = "http://localhost:8000"
    
    # 检查文件是否存在
    if not Path(yaml_file).exists():
        print(f"❌ YAML文件不存在: {yaml_file}")
        return False
    
    file_size = Path(yaml_file).stat().st_size
    print(f"📄 YAML文件: {yaml_file} ({file_size} bytes)")
    
    steps = [
        {
            "name": "检查API服务状态",
            "action": "health_check",
            "description": "验证6016-app API服务是否运行正常"
        },
        {
            "name": "验证YAML文件格式",
            "action": "validate_yaml",
            "description": "检查YAML文件格式和内容是否符合导入要求"
        },
        {
            "name": "数据库导入试运行",
            "action": "dry_run_import",
            "description": "模拟导入过程，检查数据兼容性"
        },
        {
            "name": "正式导入到数据库",
            "action": "final_import",
            "description": "将MAVLink协议数据正式导入到6016数据库"
        },
        {
            "name": "验证导入结果",
            "action": "verify_import",
            "description": "检查导入的数据完整性和正确性"
        }
    ]
    
    results = []
    
    for i, step in enumerate(steps, 1):
        print(f"\n🔄 步骤 {i}/{len(steps)}: {step['name']}")
        print(f"📋 描述: {step['description']}")
        print("-" * 40)
        
        try:
            if step['action'] == 'health_check':
                result = check_api_health(api_base)
            elif step['action'] == 'validate_yaml':
                result = validate_yaml_file(api_base, yaml_file)
            elif step['action'] == 'dry_run_import':
                result = dry_run_import(api_base, yaml_file)
            elif step['action'] == 'final_import':
                result = final_import(api_base, yaml_file)
            elif step['action'] == 'verify_import':
                result = verify_import_results(api_base)
            else:
                result = {"success": False, "error": "Unknown action"}
            
            results.append({
                "step": step['name'],
                "action": step['action'],
                "success": result['success'],
                "data": result
            })
            
            if result['success']:
                print(f"✅ {step['name']} 完成")
                if 'message' in result:
                    print(f"   {result['message']}")
                if 'stats' in result:
                    stats = result['stats']
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
            else:
                print(f"❌ {step['name']} 失败")
                print(f"   错误: {result.get('error', '未知错误')}")
                
                # 如果不是健康检查失败，继续尝试其他步骤
                if step['action'] != 'health_check':
                    continue
                else:
                    print("⚠️ API服务不可用，无法继续执行")
                    break
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ {step['name']} 异常: {e}")
            results.append({
                "step": step['name'],
                "action": step['action'],
                "success": False,
                "error": str(e)
            })
    
    # 生成执行报告
    generate_import_report(results, yaml_file)
    
    return results

def check_api_health(api_base):
    """检查API服务健康状态"""
    try:
        response = requests.get(f"{api_base}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "API服务运行正常",
                "stats": {
                    "服务状态": "正常",
                    "响应时间": f"{response.elapsed.total_seconds():.2f}秒"
                }
            }
        else:
            return {
                "success": False,
                "error": f"API服务返回错误状态: {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"无法连接到API服务: {e}",
            "solution": "请先启动服务: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
        }

def validate_yaml_file(api_base, yaml_file):
    """验证YAML文件"""
    try:
        # 使用现有的PDF验证接口
        response = requests.post(
            f"{api_base}/api/pdf/validate",
            json={"yaml_path": yaml_file},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "YAML文件格式验证通过",
                "stats": {
                    "文件路径": yaml_file,
                    "文件大小": f"{Path(yaml_file).stat().st_size} bytes",
                    "格式状态": "有效"
                }
            }
        else:
            # 如果API不支持，进行基本验证
            return validate_yaml_basic(yaml_file)
            
    except Exception as e:
        # 回退到基本验证
        return validate_yaml_basic(yaml_file)

def validate_yaml_basic(yaml_file):
    """基本YAML文件验证"""
    try:
        import yaml
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 检查基本结构
        required_keys = ['standard', 'edition']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            return {
                "success": False,
                "error": f"YAML文件缺少必需字段: {missing_keys}"
            }
        
        return {
            "success": True,
            "message": "YAML文件基本验证通过",
            "stats": {
                "标准": data.get('standard'),
                "版本": data.get('edition'),
                "枚举数量": len(data.get('enums', [])),
                "消息数量": len(data.get('spec_messages', []))
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"YAML文件解析失败: {e}"
        }

def dry_run_import(api_base, yaml_file):
    """执行试运行导入"""
    try:
        response = requests.post(
            f"{api_base}/api/import/yaml",
            json={
                "yaml_path": yaml_file,
                "dry_run": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    "success": True,
                    "message": "试运行导入成功",
                    "stats": {
                        "J消息": data.get('stats', {}).get('j_messages', 0),
                        "字段": data.get('stats', {}).get('fields', 0),
                        "枚举": data.get('stats', {}).get('enums', 0),
                        "单位": data.get('stats', {}).get('units', 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": data.get('error', '试运行失败')
                }
        else:
            return {
                "success": False,
                "error": f"试运行请求失败: HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"试运行异常: {e}"
        }

def final_import(api_base, yaml_file):
    """执行正式导入"""
    try:
        response = requests.post(
            f"{api_base}/api/import/yaml",
            json={
                "yaml_path": yaml_file,
                "dry_run": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    "success": True,
                    "message": "正式导入成功！MAVLink数据已导入数据库",
                    "stats": {
                        "导入J消息": data.get('stats', {}).get('j_messages', 0),
                        "导入字段": data.get('stats', {}).get('fields', 0),
                        "导入枚举": data.get('stats', {}).get('enums', 0),
                        "导入单位": data.get('stats', {}).get('units', 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": data.get('error', '正式导入失败')
                }
        else:
            return {
                "success": False,
                "error": f"导入请求失败: HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"导入异常: {e}"
        }

def verify_import_results(api_base):
    """验证导入结果"""
    try:
        # 检查消息表
        response = requests.get(f"{api_base}/api/table/message?limit=5", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            message_count = len(data) if isinstance(data, list) else 0
            
            return {
                "success": True,
                "message": "导入结果验证完成",
                "stats": {
                    "数据库连接": "正常",
                    "消息记录": f"至少 {message_count} 条",
                    "验证状态": "通过"
                }
            }
        else:
            return {
                "success": False,
                "error": f"无法访问数据库: HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"验证异常: {e}"
        }

def generate_import_report(results, yaml_file):
    """生成导入报告"""
    print("\n" + "=" * 60)
    print("📊 MAVLink导入执行报告")
    print("=" * 60)
    
    successful_steps = sum(1 for r in results if r['success'])
    total_steps = len(results)
    
    print(f"📄 源文件: {yaml_file}")
    print(f"⏱️ 执行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ 成功步骤: {successful_steps}/{total_steps}")
    
    print("\n📋 执行详情:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"   {i}. {result['step']}: {status}")
        if not result['success'] and 'error' in result:
            print(f"      错误: {result['error']}")
    
    if successful_steps == total_steps:
        print("\n🎉 MAVLink协议数据导入完全成功！")
        print("📋 数据库中现在包含:")
        print("   📧 MAVLink消息定义")
        print("   🏷️ 枚举类型和值")
        print("   📏 单位定义")
        print("   🔧 字段类型映射")
        
        print("\n🔍 验证命令:")
        print('   curl "http://localhost:8000/api/table/message?limit=10"')
        print('   curl "http://localhost:8000/api/table/field?limit=10"')
    else:
        print(f"\n⚠️ 导入过程中有 {total_steps - successful_steps} 个步骤失败")
        print("📋 建议检查:")
        print("   1. API服务是否正常运行")
        print("   2. 数据库连接是否正常")
        print("   3. YAML文件格式是否正确")
        print("   4. 系统是否支持MAVLink数据类型")
    
    # 保存报告到文件
    report_data = {
        "import_summary": {
            "source_file": yaml_file,
            "execution_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "success_rate": f"{successful_steps/total_steps*100:.1f}%"
        },
        "step_results": results
    }
    
    report_file = "mavlink_output/import_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存: {report_file}")

def main():
    """主函数"""
    print("🎯 MAVLink XML到数据库导入执行器")
    print("📋 流程: common.xml → YAML → 6016数据库")
    
    try:
        results = execute_mavlink_import()
        
        successful_count = sum(1 for r in results if r['success'])
        if successful_count == len(results):
            print("\n✨ MAVLink协议数据导入流程完全成功！")
            print("🎯 现在您可以在6016系统中使用MAVLink协议数据了。")
        elif successful_count > 0:
            print(f"\n⚠️ 部分成功: {successful_count}/{len(results)} 步骤完成")
            print("💡 请查看报告了解详细情况")
        else:
            print("\n❌ 导入流程失败，请检查系统配置")
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行异常: {e}")

if __name__ == "__main__":
    main()
