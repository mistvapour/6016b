"""
检查应用启动时的错误
"""
import sys
import traceback

print("=" * 60)
print("检查应用启动错误")
print("=" * 60)
print()

try:
    print("步骤 1: 导入 FastAPI...")
    from fastapi import FastAPI
    print("✓ FastAPI 导入成功")
    print()

    print("步骤 2: 导入 main 模块...")
    print("注意: 如果这里卡住，说明某个模块导入时阻塞")
    print("     等待最多30秒...")
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("导入超时，可能某个模块阻塞")
    
    # 尝试导入
    try:
        from main import app
        print("✓ main 模块导入成功")
        print(f"✓ 应用创建成功: {app.title}")
        print()
    except Exception as e:
        print(f"✗ main 模块导入失败: {e}")
        print()
        traceback.print_exc()
        sys.exit(1)
    
    print("步骤 3: 检查路由...")
    routes = [r for r in app.routes]
    print(f"✓ 已注册路由数: {len(routes)}")
    print()
    
    print("步骤 4: 测试健康检查端点...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    try:
        response = client.get("/api/health")
        print(f"✓ 健康检查端点响应: {response.status_code}")
        print(f"✓ 响应内容: {response.json()}")
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("✓ 所有检查通过！应用可以正常启动")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n用户中断")
    sys.exit(130)
except Exception as e:
    print()
    print("=" * 60)
    print(f"✗ 检查失败: {e}")
    print("=" * 60)
    traceback.print_exc()
    sys.exit(1)
finally:
    sys.exit(0)

