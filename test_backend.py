#!/usr/bin/env python3
"""
后端API测试脚本
"""
import requests
import json
import time

def test_api_health():
    """测试API健康检查"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/health', timeout=5)
        print(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"健康检查响应: {response.json()}")
            return True
        else:
            print(f"健康检查失败: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("无法连接到后端服务 (127.0.0.1:8000)")
        return False
    except Exception as e:
        print(f"健康检查出错: {e}")
        return False

def test_api_endpoints():
    """测试其他API端点"""
    endpoints = [
        '/api/v2/health',
        '/api/specs',
        '/api/messages',
        '/api/v2/statistics'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:8000{endpoint}', timeout=5)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  响应: {response.json()}")
        except Exception as e:
            print(f"{endpoint}: 错误 - {e}")

if __name__ == "__main__":
    print("开始测试后端API...")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试健康检查
    if test_api_health():
        print("\n✅ 后端服务运行正常!")
        print("\n测试其他端点...")
        test_api_endpoints()
    else:
        print("\n❌ 后端服务无法访问")
        print("请检查:")
        print("1. 后端服务是否已启动")
        print("2. 端口8000是否被占用")
        print("3. 防火墙设置")
