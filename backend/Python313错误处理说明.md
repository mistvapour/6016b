# 🔧 Python 3.13 致命错误处理说明

## ❌ 错误信息

```
*** fatal error - Internal error: TP_NUM_C_BUFS too small: 50
```

## 🔍 问题分析

这是 Python 3.13 的内部致命错误，发生在导入 `universal_import_api` 模块时。

**根本原因：**
- Python 3.13 是较新版本，某些 C 扩展库可能不兼容
- PyMuPDF (fitz) 在 `universal_import_system.py` 中被导入
- 即使使用延迟导入，导入 `universal_import_api` 模块本身仍可能触发问题

## ✅ 已实施的修复

### 1. 延迟导入 UniversalImportSystem

在 `universal_import_api.py` 中：
- 移除了文件顶部的 `from universal_import_system import UniversalImportSystem`
- 改为在 `get_universal_system()` 函数内部延迟导入

### 2. 增强异常捕获

在 `main.py` 中：
- 添加了更全面的异常捕获（ImportError, SystemError, Exception）
- 特别处理 Python 3.13 兼容性问题
- 提供友好的错误提示

## 🎯 如果仍然崩溃

如果 Python 解释器仍然崩溃（无法捕获的致命错误），可以使用以下方案：

### 方案 1: 暂时完全禁用 Universal API

在 `main.py` 中直接设置：

```python
# 暂时禁用 Universal API 模块
UNIVERSAL_API_AVAILABLE = False
print("⚠️  Universal API模块已暂时禁用（Python 3.13 兼容性问题）", file=sys.stderr)
```

### 方案 2: 使用 Python 3.11 或 3.12

推荐使用更稳定的 Python 版本：

```bash
# 创建新的虚拟环境，使用 Python 3.11 或 3.12
python3.11 -m venv .venv
# 或
python3.12 -m venv .venv
```

### 方案 3: 更新依赖包

尝试更新可能有问题的包：

```bash
pip install --upgrade PyMuPDF opencv-python numpy
```

## 📋 当前状态

- ✅ 已实现延迟导入
- ✅ 已增强异常捕获
- ⚠️  如果仍然崩溃，请考虑暂时禁用模块或更换 Python 版本

## 🚀 测试

重新启动服务：

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

如果仍然崩溃，说明需要暂时禁用 Universal API 模块。


