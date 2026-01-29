# PowerShell 脚本：在新窗口中启动后端服务
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = $scriptPath

Write-Host "========================================" -ForegroundColor Green
Write-Host "  启动 MIL-STD-6016 后端服务" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 切换到后端目录
Set-Location $backendPath
Write-Host "当前目录: $backendPath" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
$venvPath = Join-Path $backendPath ".venv\Scripts\activate.bat"
if (-not (Test-Path $venvPath)) {
    Write-Host "错误: 虚拟环境不存在" -ForegroundColor Red
    Write-Host "路径: $venvPath" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host "正在新窗口中启动服务..." -ForegroundColor Yellow
Write-Host ""

# 构建启动命令
$startupCmd = @"
cd /d "$backendPath" && call .venv\Scripts\activate.bat && echo ======================================== && echo    MIL-STD-6016 后端服务 && echo ======================================== && echo. && echo 服务地址: http://127.0.0.1:8000 && echo API文档: http://127.0.0.1:8000/docs && echo 健康检查: http://127.0.0.1:8000/api/health && echo. && echo 提示: 按 Ctrl+C 可停止服务 && echo ======================================== && echo. && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
"@

# 在新窗口中启动
Start-Process cmd.exe -ArgumentList "/k", $startupCmd -WindowStyle Normal

Write-Host "✓ 已在新窗口中启动服务" -ForegroundColor Green
Write-Host ""
Write-Host "请查看新打开的窗口" -ForegroundColor Cyan
Write-Host "等待 10 秒后，可以访问:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host ""
Read-Host "按 Enter 键退出"

