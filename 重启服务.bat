@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 重启前后端服务
echo ========================================
echo.

echo [步骤 1] 停止现有服务...
echo.

REM 停止后端服务 (端口 8000)
echo 检查后端服务 (端口 8000)...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   发现进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    echo   后端服务已停止
)

REM 停止前端服务 (端口 5173)
echo 检查前端服务 (端口 5173)...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo   发现进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    echo   前端服务已停止
)

echo 等待服务完全停止...
timeout /t 3 /nobreak >nul

echo.
echo [步骤 2] 启动后端服务 (端口 8000)...
start "后端服务 - 端口 8000" cmd /k "title 后端服务 && call venv\Scripts\activate.bat && cd backend && echo 正在启动后端服务... && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo [步骤 3] 启动前端服务 (端口 5173)...
start "前端服务 - 端口 5173" cmd /k "title 前端服务 && cd frontend && echo 正在启动前端服务... && npm run dev"

echo.
echo ========================================
echo 服务重启完成！
echo ========================================
echo 后端 API: http://localhost:8000
echo 后端文档: http://localhost:8000/docs
echo 前端应用: http://localhost:5173
echo.
echo 服务运行在独立的窗口中：
echo - 后端服务窗口标题: "后端服务 - 端口 8000"
echo - 前端服务窗口标题: "前端服务 - 端口 5173"
echo.
echo 关闭对应的窗口即可停止对应的服务
echo ========================================
echo.
pause
