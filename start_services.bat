@echo off
echo ========================================
echo 启动前后端服务
echo ========================================
echo.

echo [1/2] 启动后端服务 (端口 8000)...
start "后端服务" cmd /k "call venv\Scripts\activate.bat && cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo [2/2] 启动前端服务 (端口 5173)...
start "前端服务" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo 后端 API: http://localhost:8000
echo 后端文档: http://localhost:8000/docs
echo 前端应用: http://localhost:5173
echo.
echo 注意：服务运行在独立的窗口中，关闭窗口即可停止服务
echo ========================================
pause

