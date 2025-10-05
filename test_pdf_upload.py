#!/usr/bin/env python3
"""
测试PDF上传功能的脚本
"""
import requests
import json

def test_pdf_upload():
    """测试PDF上传API"""
    url = "http://127.0.0.1:8000/api/pdf/upload"
    
    # 测试文件路径
    test_file = "test_sample/link16-import.pdf"
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            data = {
                'standard': 'MIL-STD-6016',
                'edition': 'B'
            }
            
            print(f"正在上传文件: {test_file}")
            response = requests.post(url, files=files, data=data)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ PDF上传成功!")
                print(f"消息: {result.get('message', 'N/A')}")
                
                if result.get('success') and result.get('data'):
                    data = result['data']
                    print(f"消息类型: {data.get('sim', {}).get('message_type', 'N/A')}")
                    print(f"字段数量: {len(data.get('sim', {}).get('fields', []))}")
                    
                    # 显示字段信息
                    fields = data.get('sim', {}).get('fields', [])
                    for i, field in enumerate(fields, 1):
                        print(f"  字段 {i}: {field.get('field_name', 'N/A')} "
                              f"({field.get('bit_range', {}).get('start', 0)}-{field.get('bit_range', {}).get('end', 0)})")
                    
                    # 显示验证结果
                    validation = data.get('validation_result', {})
                    print(f"验证结果: {'✅ 有效' if validation.get('valid') else '❌ 无效'}")
                    print(f"覆盖率: {validation.get('coverage', 0):.1%}")
                    print(f"置信度: {validation.get('confidence', 0):.1%}")
                    
            else:
                print(f"❌ PDF上传失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
    except FileNotFoundError:
        print(f"❌ 测试文件不存在: {test_file}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_health():
    """测试健康检查"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/health")
        if response.status_code == 200:
            print("✅ 后端服务健康检查通过")
            return True
        else:
            print(f"❌ 后端服务健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试PDF上传功能...")
    print("=" * 50)
    
    # 先测试健康检查
    if test_health():
        print()
        test_pdf_upload()
    
    print("=" * 50)
    print("测试完成!")
