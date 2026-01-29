@echo off
chcp 65001 >nul
title 后端服务 - 测试版本
echo ========================================
echo   启动测试版本后端服务
echo   使用 main_test.py（简化版）
echo ========================================
echo.

cd /d %~dp0

echo [步骤 1] 激活虚拟环境...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat >nul 2>&1
    echo ✓ 虚拟环境已激活
) else (
    echo ✗ 错误: 虚拟环境不存在
    pause
    exit /b 1
)

echo.
echo [步骤 2] 启动测试版本服务...
echo ========================================
echo 服务地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo 健康检查: http://127.0.0.1:8000/api/health
echo 测试端点: http://127.0.0.1:8000/api/test
echo ========================================
echo.
echo 提示: 这是测试版本，只包含基本功能
echo       如果测试版本能正常启动，说明基础配置没问题
echo       然后可以逐步添加功能到主版本
echo.
echo 正在启动...
echo.

python -m uvicorn main_test:app --host 127.0.0.1 --port 8000 --reload

pause

