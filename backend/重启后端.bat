@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 重启后端服务
echo ========================================
echo.

echo [步骤 1] 停止现有后端服务...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   停止进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo 等待端口释放...
timeout /t 2 /nobreak >nul

echo.
echo [步骤 2] 启动后端服务...
start "后端服务 - 端口 8000" cmd /k "title 后端服务 && call .venv\Scripts\activate.bat && echo ======================================== && echo 后端服务启动中... && echo ======================================== && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo ========================================
echo 后端服务重启完成！
echo ========================================
echo 后端 API: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 服务运行在独立窗口中
echo ========================================
timeout /t 2 /nobreak >nul

