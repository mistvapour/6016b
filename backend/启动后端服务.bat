@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "MIL-STD-6016 后端服务" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && echo ======================================== && echo    MIL-STD-6016 后端服务 && echo ======================================== && echo. && echo 服务地址: http://127.0.0.1:8000 && echo API文档: http://127.0.0.1:8000/docs && echo 健康检查: http://127.0.0.1:8000/api/health && echo. && echo 提示: 按 Ctrl+C 可停止服务 && echo ======================================== && echo. && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
echo.
echo ========================================
echo 正在新窗口中启动后端服务...
echo ========================================
echo.
echo 服务将在新打开的窗口中运行
echo 请查看新窗口的启动信息
echo.
echo 等待 10 秒后，可以访问:
echo   http://127.0.0.1:8000/docs
echo.
timeout /t 3 >nul

