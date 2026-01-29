# 🚨 紧急方案：暂时禁用 Universal API 模块

## ❌ 问题

Python 3.13 致命错误导致服务无法启动：
```
*** fatal error - Internal error: TP_NUM_C_BUFS too small: 50
```

这是一个无法通过 try-except 捕获的致命错误，会导致 Python 进程直接崩溃。

## ✅ 立即解决方案

### 在 main.py 中暂时禁用 Universal API 模块

找到 `main.py` 中的这部分代码（大约第 39-51 行）：

```python
print(">>> 正在加载 Universal API 模块...", file=sys.stderr)
try:
    from universal_import_api import include_universal_routes
    UNIVERSAL_API_AVAILABLE = True
    print("✅ Universal API模块加载成功", file=sys.stderr)
except ...:
    ...
```

**替换为：**

```python
# 暂时禁用 Universal API 模块（Python 3.13 兼容性问题）
UNIVERSAL_API_AVAILABLE = False
print("⚠️  Universal API模块已暂时禁用（Python 3.13 兼容性问题）", file=sys.stderr)
print("   错误: TP_NUM_C_BUFS too small: 50", file=sys.stderr)
print("   建议: 使用 Python 3.11 或 3.12，或等待相关库更新", file=sys.stderr)
```

这样服务就能正常启动，只是 Universal API 功能不可用。

## 🎯 长期解决方案

1. **使用 Python 3.11 或 3.12**（推荐）
2. 等待 PyMuPDF 等库更新以支持 Python 3.13
3. 或者移除对 PyMuPDF 的依赖，使用其他 PDF 处理库

## 📋 验证

禁用后，服务应该能正常启动，其他功能不受影响。


