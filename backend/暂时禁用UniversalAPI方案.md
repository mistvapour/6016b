# 🔧 暂时禁用 Universal API 方案

## ❌ 问题

Python 3.13 致命错误：
```
*** fatal error - Internal error: TP_NUM_C_BUFS too small: 50
```

这个错误在导入 `universal_import_api` 模块时发生，可能是由于：
- PyMuPDF (fitz) 与 Python 3.13 不兼容
- 其他 C 扩展库的兼容性问题

## ✅ 解决方案：暂时禁用 Universal API 模块

### 方法 1: 在 main.py 中禁用（推荐）

修改 `main.py`，跳过 Universal API 模块的导入：

```python
# 暂时禁用 Universal API 模块
UNIVERSAL_API_AVAILABLE = False
print("⚠️  Universal API模块已暂时禁用（Python 3.13 兼容性问题）", file=sys.stderr)

# 注释掉导入部分
# print(">>> 正在加载 Universal API 模块...", file=sys.stderr)
# try:
#     from universal_import_api import include_universal_routes
#     UNIVERSAL_API_AVAILABLE = True
#     print("✅ Universal API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ Universal API模块导入失败: {e}", file=sys.stderr)
#     UNIVERSAL_API_AVAILABLE = False
```

### 方法 2: 添加异常捕获

在 `main.py` 中捕获所有异常：

```python
print(">>> 正在加载 Universal API 模块...", file=sys.stderr)
try:
    from universal_import_api import include_universal_routes
    UNIVERSAL_API_AVAILABLE = True
    print("✅ Universal API模块加载成功", file=sys.stderr)
except Exception as e:  # 捕获所有异常，不仅仅是 ImportError
    print(f"❌ Universal API模块导入失败: {e}", file=sys.stderr)
    print(f"   类型: {type(e).__name__}", file=sys.stderr)
    UNIVERSAL_API_AVAILABLE = False
```

## 🎯 建议

1. **立即操作**：使用方法 2，添加更广泛的异常捕获，让服务能启动
2. **长期方案**：
   - 考虑使用 Python 3.11 或 3.12
   - 或者等待相关库更新以支持 Python 3.13

## 📋 验证

禁用后，服务应该能正常启动，只是 Universal API 功能不可用。


