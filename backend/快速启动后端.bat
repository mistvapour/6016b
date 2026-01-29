@echo off
chcp 65001 >nul
echo ========================================
echo 快速启动后端服务
echo ========================================
echo.

cd /d %~dp0

echo [步骤 1] 激活虚拟环境...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo 错误: 虚拟环境不存在，请先创建虚拟环境
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
echo 服务地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo.
echo 按 Ctrl+C 可停止服务
echo ========================================
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause

