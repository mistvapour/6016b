@echo off
echo ========================================
echo 停止前后端服务
echo ========================================
echo.

echo 正在查找并停止占用端口 8000 和 5173 的进程...
echo.

REM 停止后端服务 (端口 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [后端] 发现进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo [后端] 进程已停止
    ) else (
        echo [后端] 停止失败或进程不存在
    )
)

REM 停止前端服务 (端口 5173)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo [前端] 发现进程 PID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo [前端] 进程已停止
    ) else (
        echo [前端] 停止失败或进程不存在
    )
)

echo.
echo 正在查找 Python 和 Node 进程...

REM 尝试通过进程名停止（可选）
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo.
echo ========================================
echo 服务停止完成！
echo ========================================
timeout /t 2 /nobreak >nul


