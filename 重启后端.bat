@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 重启后端服务
echo ========================================
echo.

echo [步骤 1] 停止现有后端服务...
echo 检查端口 8000 是否被占用...

REM 查找并停止占用端口8000的进程
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   发现后端服务进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 后端服务已停止
    ) else (
        echo   ✗ 停止失败
    )
)

echo 等待进程完全释放...
timeout /t 2 /nobreak >nul

echo.
echo [步骤 2] 启动后端服务 (端口 8000)...
start "后端服务 - 端口 8000" cmd /k "title 后端服务 && call venv\Scripts\activate.bat && cd backend && echo ======================================== && echo 后端服务启动中... && echo ======================================== && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 后端服务重启完成！
echo ========================================
echo 后端 API: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/api/health
echo.
echo 服务运行在独立窗口中，关闭窗口即可停止服务
echo ========================================
echo.
timeout /t 2 /nobreak >nul


