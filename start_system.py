#!/usr/bin/env python3
"""
PDF处理系统启动脚本
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("检查系统依赖...")
    
    # 检查Python依赖
    try:
        import fastapi
        import uvicorn
        import PyMuPDF
        import pdfplumber
        import camelot
        import yaml
        import numpy
        import pandas
        print("✓ Python依赖检查通过")
    except ImportError as e:
        print(f"✗ Python依赖缺失: {e}")
        print("请运行: pip install -r backend/requirements.txt")
        return False
    
    # 检查Node.js依赖
    frontend_path = Path("frontend")
    if frontend_path.exists():
        try:
            result = subprocess.run(["npm", "list"], cwd=frontend_path, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Node.js依赖检查通过")
            else:
                print("✗ Node.js依赖缺失")
                print("请运行: cd frontend && npm install")
                return False
        except FileNotFoundError:
            print("✗ Node.js未安装或npm命令不可用")
            return False
    
    return True

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    backend_path = Path("backend")
    
    try:
        # 启动FastAPI服务
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=backend_path)
        
        print("✓ 后端服务启动成功 (http://localhost:8000)")
        return process
    except Exception as e:
        print(f"✗ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    frontend_path = Path("frontend")
    
    try:
        # 启动Vite开发服务器
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_path)
        
        print("✓ 前端服务启动成功 (http://localhost:5173)")
        return process
    except Exception as e:
        print(f"✗ 前端服务启动失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("PDF处理系统启动器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n依赖检查失败，请先安装所需依赖")
        return
    
    print("\n开始启动服务...")
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        return
    
    # 等待后端启动
    time.sleep(3)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("系统启动完成!")
    print("=" * 60)
    print("前端地址: http://localhost:5173")
    print("后端API: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        
        # 停止前端
        if frontend_process:
            frontend_process.terminate()
            print("✓ 前端服务已停止")
        
        # 停止后端
        if backend_process:
            backend_process.terminate()
            print("✓ 后端服务已停止")
        
        print("系统已完全停止")

if __name__ == "__main__":
    main()
