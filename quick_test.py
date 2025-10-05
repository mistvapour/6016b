#!/usr/bin/env python3
"""
快速API测试脚本
"""
import urllib.request
import json

def test_api():
    """测试API端点"""
    try:
        # 测试健康检查
        url = "http://127.0.0.1:8000/api/health"
        print(f"测试: {url}")
        
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read().decode('utf-8')
            result = json.loads(data)
            print(f"✅ 成功! 状态码: {response.status}")
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

def test_multiple_endpoints():
    """测试多个端点"""
    endpoints = [
        "/api/health",
        "/api/v2/health", 
        "/api/specs",
        "/api/messages",
        "/api/v2/statistics",
        "/"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"http://127.0.0.1:8000{endpoint}"
            print(f"\n测试: {url}")
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                print(f"✅ 成功! 状态码: {response.status}")
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                
        except Exception as e:
            print(f"❌ 失败: {e}")

if __name__ == "__main__":
    print("开始快速API测试...")
    print("=" * 50)
    
    if test_api():
        print("\n🎉 基础API测试通过!")
        print("\n测试其他端点...")
        test_multiple_endpoints()
    else:
        print("\n💥 API测试失败")
        print("请检查后端服务是否正在运行")
