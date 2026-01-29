# 🔧 解决 Python 3.13 内部错误

## ❌ 错误信息

```
*** fatal error - Internal error: TP_NUM_C_BUFS too small: 50
```

## 🔍 原因分析

这是一个 Python 3.13 的内部错误，通常由以下原因导致：

1. **Python 3.13 版本问题** - Python 3.13 是较新版本，可能与某些 C 扩展库不兼容
2. **PyMuPDF (fitz) 兼容性** - PyMuPDF 可能与 Python 3.13 有兼容性问题
3. **其他 C 扩展库** - opencv-python, numpy 等也可能有问题

## ✅ 解决方案

### 方案 1: 延迟导入问题模块（推荐）

修改 `universal_import_api.py`，延迟导入 `universal_import_system`：

```python
# 修改前（导入时就加载）
from universal_import_system import UniversalImportSystem

# 修改后（延迟导入）
def get_universal_system():
    global _universal_system
    if _universal_system is None:
        from universal_import_system import UniversalImportSystem
        _universal_system = UniversalImportSystem()
    return _universal_system
```

### 方案 2: 暂时禁用 Universal API 模块

如果暂时不需要 Universal API 功能，可以在 `main.py` 中注释掉：

```python
# try:
#     from universal_import_api import include_universal_routes
#     UNIVERSAL_API_AVAILABLE = True
# except ImportError as e:
#     print(f"Universal API模块导入失败: {e}")
#     UNIVERSAL_API_AVAILABLE = False
UNIVERSAL_API_AVAILABLE = False
```

### 方案 3: 降级 Python 版本（长期方案）

考虑使用 Python 3.11 或 3.12，这些版本更稳定，兼容性更好。

### 方案 4: 更新依赖包

尝试更新可能有问题的包：

```bash
pip install --upgrade PyMuPDF opencv-python numpy
```

## 🎯 立即可以做的

1. **暂时禁用 Universal API 模块** - 让其他功能先运行
2. **使用延迟导入** - 避免导入时就加载有问题模块
3. **检查 Python 版本** - 考虑使用更稳定的版本

## 📋 建议

如果不需要立即使用 Universal API 功能，可以：
1. 暂时注释掉 Universal API 模块
2. 先让服务能正常启动
3. 之后再单独解决 Universal API 的问题


