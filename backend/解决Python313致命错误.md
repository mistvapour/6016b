# 🔧 解决 Python 3.13 致命错误

## ❌ 错误信息

```
*** fatal error - Internal error: TP_NUM_C_BUFS too small: 50
```

## 🔍 原因分析

这是 Python 3.13 的内部错误，通常由以下原因导致：

1. **Python 3.13 兼容性问题** - Python 3.13 是较新版本，某些 C 扩展库可能不兼容
2. **PyMuPDF (fitz) 问题** - `universal_import_system.py` 导入了 `fitz`，可能与 Python 3.13 不兼容
3. **C 扩展库冲突** - opencv-python, numpy 等 C 扩展库可能有兼容性问题

## ✅ 已实施的修复

### 1. 延迟导入 UniversalImportSystem

修改了 `universal_import_api.py`，将导入从文件顶部移到函数内部：

**修改前：**
```python
from universal_import_system import UniversalImportSystem  # 在文件顶部导入
```

**修改后：**
```python
# 不在文件顶部导入
def get_universal_system():
    # 在函数内部延迟导入
    from universal_import_system import UniversalImportSystem
    ...
```

这样，`universal_import_system` 模块（包含 PyMuPDF）只在需要时才导入，避免在导入 `universal_import_api` 时就触发错误。

## 🎯 其他解决方案

### 方案 1: 暂时禁用 Universal API 模块

如果延迟导入仍然有问题，可以暂时禁用：

在 `main.py` 中：
```python
# UNIVERSAL_API_AVAILABLE = True  # 暂时禁用
UNIVERSAL_API_AVAILABLE = False
```

### 方案 2: 使用更稳定的 Python 版本

考虑使用 Python 3.11 或 3.12，这些版本更稳定。

### 方案 3: 更新依赖包

尝试更新可能有问题的包：
```bash
pip install --upgrade PyMuPDF opencv-python numpy
```

## 🚀 测试

修复后，重新启动服务：

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

现在应该能通过 Universal API 模块的加载了！

## 📋 如果仍然有问题

如果延迟导入仍然有问题，可以：

1. **暂时禁用 Universal API 模块** - 让其他功能先运行
2. **检查具体错误信息** - 看是哪个模块导致问题
3. **考虑降级 Python 版本** - 使用 Python 3.11 或 3.12


