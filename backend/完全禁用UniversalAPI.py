# 完全禁用 Universal API 模块的方案
# 如果 Python 3.13 兼容性问题持续存在，可以使用这个方案

# 在 main.py 中替换 Universal API 导入部分为：

"""
# 暂时禁用 Universal API 模块（Python 3.13 兼容性问题）
UNIVERSAL_API_AVAILABLE = False
print("⚠️  Universal API模块已暂时禁用（Python 3.13 兼容性问题）", file=sys.stderr)
print("   错误信息: TP_NUM_C_BUFS too small: 50", file=sys.stderr)
print("   建议: 使用 Python 3.11 或 3.12", file=sys.stderr)

# 注释掉原来的导入代码：
# print(">>> 正在加载 Universal API 模块...", file=sys.stderr)
# try:
#     from universal_import_api import include_universal_routes
#     UNIVERSAL_API_AVAILABLE = True
#     print("✅ Universal API模块加载成功", file=sys.stderr)
# except Exception as e:
#     print(f"❌ Universal API模块导入失败: {e}", file=sys.stderr)
#     UNIVERSAL_API_AVAILABLE = False
"""


