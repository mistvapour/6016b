@echo off
chcp 65001 >nul
title 后端服务 - MIL-STD-6016 API
echo ========================================
echo 直接启动后端服务（跳过导入测试）
echo ========================================
echo.

cd /d %~dp0

echo [步骤 1] 激活虚拟环境...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo 错误: 虚拟环境不存在
    pause
    exit /b 1
)

echo.
echo [步骤 2] 检查依赖...
python -c "import fastapi, uvicorn; print('✓ 依赖检查通过')" 2>nul
if errorlevel 1 (
    echo 错误: 依赖未安装，请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [步骤 3] 启动后端服务...
echo ========================================
echo 服务地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo 健康检查: http://127.0.0.1:8000/api/health
echo ========================================
echo.
echo 提示: 服务启动后，访问 http://127.0.0.1:8000/docs 查看API文档
echo 按 Ctrl+C 可停止服务
echo.
echo 正在启动...
echo.

REM 直接启动，不进行导入测试
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause

