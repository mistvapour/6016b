@echo off
echo ========================================
echo 启动后端服务
echo ========================================
echo.

echo [步骤 1] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo [步骤 2] 启动后端服务...
echo 服务将运行在: http://localhost:8000
echo 按 Ctrl+C 可停止服务
echo.
echo ========================================

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause

