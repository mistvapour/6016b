# 🔧 解决 "Could not import module 'main'" 错误

## ❌ 错误信息

```
ERROR:    Error loading ASGI app. Could not import module "main".
```

## 🔍 原因分析

这个错误通常发生在：

1. **工作目录不对** - uvicorn 不在 `backend` 目录下运行
2. **模块导入失败** - `main.py` 在导入时出错
3. **路径问题** - Python 找不到模块

## ✅ 解决方案

### 方案 1: 确保在正确的目录运行（最重要！）

**错误的方式**（在项目根目录运行）：
```bash
cd C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app
python -m uvicorn main:app  # ❌ 错误，main.py 在 backend 目录
```

**正确的方式**（在 backend 目录运行）：
```bash
cd C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload  # ✅ 正确
```

### 方案 2: 使用完整路径

如果必须在项目根目录运行，使用完整路径：

```bash
cd C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 方案 3: 检查 main.py 是否有语法错误

```bash
cd backend
python -m py_compile main.py
```

### 方案 4: 测试导入

```bash
cd backend
python -c "from main import app; print('✓ 导入成功')"
```

如果有错误，查看具体错误信息。

## 🚀 正确的启动步骤

### 步骤 1: 打开新的终端窗口

### 步骤 2: 切换到 backend 目录

```bash
cd C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\backend
```

### 步骤 3: 激活虚拟环境

```bash
source .venv/Scripts/activate
```

### 步骤 4: 启动服务

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## 📋 验证

启动后应该看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

如果看到 `Application startup complete`，说明导入成功！

## ⚠️ 重要提示

- **必须在 backend 目录下运行 uvicorn**
- **或者使用完整路径 `backend.main:app`**
- **确保虚拟环境已激活**

