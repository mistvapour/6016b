@echo off
chcp 65001 >nul
echo ========================================
echo 快速测试导入 main.py
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
echo [步骤 2] 测试导入...
echo 如果卡住，请按 Ctrl+C 强制退出
echo ========================================
echo.

python 测试导入.py

echo.
echo ========================================
echo 测试完成
echo ========================================
pause

