@echo off
chcp 65001 >nul
title 后端服务 - MIL-STD-6016 API
color 0A
echo ========================================
echo   紧急启动后端服务
echo   （跳过所有测试，直接启动）
echo ========================================
echo.

cd /d %~dp0

echo [激活虚拟环境]
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat >nul 2>&1
    echo ✓ 虚拟环境已激活
) else (
    echo ✗ 错误: 虚拟环境不存在
    echo   请先创建虚拟环境
    pause
    exit /b 1
)

echo.
echo [启动后端服务]
echo ========================================
echo 服务地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo 健康检查: http://127.0.0.1:8000/api/health
echo ========================================
echo.
echo 提示: 
echo   - 如果启动失败，请检查错误信息
echo   - 如果卡住，请关闭窗口后重新启动
echo   - 服务启动后，在浏览器访问上述地址
echo.
echo 正在启动，请稍候...
echo.

REM 直接启动，不进行任何导入测试
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause

