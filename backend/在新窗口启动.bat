@echo off
REM 在新窗口中启动后端服务
start "后端服务 - MIL-STD-6016 API" cmd /k "cd /d %~dp0 && .venv\Scripts\activate.bat && echo ======================================== && echo   后端服务已启动 && echo ======================================== && echo. && echo 服务地址: http://127.0.0.1:8000 && echo API文档: http://127.0.0.1:8000/docs && echo 健康检查: http://127.0.0.1:8000/api/health && echo. && echo 按 Ctrl+C 可停止服务 && echo ======================================== && echo. && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

