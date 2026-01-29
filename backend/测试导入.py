"""
安全的导入测试脚本
使用 sys.exit() 确保立即退出，避免阻塞

使用方法：
    python 测试导入.py

如果卡住，按 Ctrl+C 强制退出
"""
import sys
import signal

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print("\n\n收到中断信号，强制退出...")
    sys.exit(130)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)

print("=" * 60)
print("开始测试导入 main.py...")
print("=" * 60)
print()

try:
    print("步骤 1: 正在导入 app...")
    from main import app
    print(f"✓ 导入成功！")
    print()
    
    print("步骤 2: 检查应用信息...")
    print(f"✓ 应用名称: {app.title}")
    print(f"✓ 应用版本: {app.version}")
    print()
    
    print("步骤 3: 检查路由数量...")
    routes_count = len([r for r in app.routes])
    print(f"✓ 已注册路由数: {routes_count}")
    print()
    
    print("=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n\n用户中断")
    sys.exit(130)
except Exception as e:
    print(f"\n✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # 强制退出，避免任何后台线程或连接导致阻塞
    print("\n测试完成，正在退出...")
    sys.exit(0)

