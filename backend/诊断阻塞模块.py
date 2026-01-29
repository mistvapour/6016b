"""
诊断哪个模块导致导入阻塞
逐步导入每个模块，找出阻塞点
"""
import sys
import time

def test_import(module_name, import_code):
    """测试导入单个模块"""
    print(f"\n{'='*60}")
    print(f"测试: {module_name}")
    print(f"{'='*60}")
    try:
        start_time = time.time()
        exec(import_code)
        elapsed = time.time() - start_time
        print(f"✓ {module_name} 导入成功 (耗时: {elapsed:.2f}秒)")
        return True, elapsed
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print(f"✗ {module_name} 导入失败: {e}")
        return False, elapsed

print("开始诊断导入阻塞问题...")
print("如果某个模块卡住超过10秒，将提示超时")
print("\n注意: 如果卡住，请关闭终端窗口重新打开")

results = []

# 测试 1: 基础模块
print("\n[测试组 1] 基础 Python 模块")
test_import("基础模块", "import os, io, csv, logging, re")

# 测试 2: FastAPI
print("\n[测试组 2] FastAPI 框架")
test_import("FastAPI", "from fastapi import FastAPI")
test_import("CORSMiddleware", "from fastapi.middleware.cors import CORSMiddleware")
test_import("StreamingResponse", "from fastapi.responses import StreamingResponse")

# 测试 3: Pydantic
print("\n[测试组 3] Pydantic")
test_import("Pydantic", "from pydantic import BaseModel")

# 测试 4: 数据库模块（可能阻塞）
print("\n[测试组 4] 数据库模块（可能阻塞）")
print("提示: 如果这里卡住，说明 db.py 在导入时尝试连接数据库")
result, elapsed = test_import("db模块", """
try:
    from db import call_proc, query, exec_sql
    print("  -> 数据库模块可用")
except ImportError as e:
    print(f"  -> 数据库模块不可用: {e}")
""")
if elapsed > 5:
    print("⚠️  警告: db模块导入耗时超过5秒，可能在连接数据库")

# 测试 5: API 模块（逐个测试）
print("\n[测试组 5] API 模块")
api_modules = [
    ("pdf_api", "from pdf_api import include_pdf_routes"),
    ("mqtt_api", "from mqtt_api import router as mqtt_router"),
    ("universal_import_api", "from universal_import_api import include_universal_routes"),
    ("semantic_interop_api", "from semantic_interop_api import include_semantic_routes"),
    ("cdm_api", "from cdm_api import include_cdm_routes"),
    ("unified_api", "from unified_api import include_unified_routes"),
    ("message_generation_api", "from message_generation_api import include_message_generation_routes"),
]

for module_name, import_code in api_modules:
    result, elapsed = test_import(module_name, import_code)
    if elapsed > 5:
        print(f"⚠️  警告: {module_name} 导入耗时超过5秒")
    if elapsed > 10:
        print(f"❌ 严重: {module_name} 导入耗时超过10秒，可能阻塞")

# 测试 6: 完整导入 main
print("\n[测试组 6] 完整导入 main.py")
print("提示: 如果这里卡住，说明 main.py 中有阻塞代码")
result, elapsed = test_import("main模块", """
try:
    from main import app
    print(f"  -> app 创建成功: {app.title}")
except Exception as e:
    print(f"  -> 导入失败: {e}")
""")

print("\n" + "="*60)
print("诊断完成！")
print("="*60)
print("\n总结:")
print("- 如果某个模块耗时超过5秒，可能需要优化")
print("- 如果某个模块卡住不退出，说明有阻塞代码")
print("\n建议:")
print("1. 如果 db 模块阻塞，检查 db.py 是否在模块级别连接数据库")
print("2. 如果 API 模块阻塞，检查是否有后台线程或网络连接")
print("3. 直接使用 uvicorn 启动服务，通常不会阻塞")

sys.exit(0)

