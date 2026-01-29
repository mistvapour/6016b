# 🔍 main.py 启动问题分析

## ❌ 问题：直接运行 `python main.py` 导致 Segmentation fault

### 原因分析

在 `main.py` 的第 704 行：

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
```

**问题所在：**

1. **reload=True 的问题**：
   - 当直接运行 `python main.py` 时，`reload=True` 会导致 uvicorn 尝试监控文件变化并重新加载
   - 在 Windows 的 Git Bash 环境下，这可能引发 Segmentation fault

2. **直接运行 vs 模块运行**：
   - `python main.py` - 直接执行脚本，reload 机制可能有问题
   - `python -m uvicorn main:app` - 作为模块运行，更稳定

3. **Windows 环境兼容性**：
   - Windows 下的文件监控机制可能导致崩溃

## ✅ 解决方案

### 方案 1: 修改 main.py 的启动代码（推荐）

将 `reload=True` 改为 `reload=False` 或仅在开发环境启用：

```python
if __name__ == "__main__":
    import uvicorn
    import os
    
    # 只在开发环境启用 reload
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        reload=reload
    )
```

### 方案 2: 完全移除 `if __name__ == "__main__"` 块（最推荐）

直接删除这个块，强制使用 `python -m uvicorn` 方式启动，这样更符合 FastAPI 的最佳实践。

### 方案 3: 使用正确的启动命令

**永远使用这种方式启动：**
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**不要使用：**
```bash
python main.py  # ❌ 这会导致 Segmentation fault
```

## 🔧 推荐的修复

修改 `main.py` 文件末尾的启动代码。


