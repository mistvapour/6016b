#!/bin/bash
# 启动后端服务

cd /Users/feilubi/Documents/GitHub/6016b

echo "启动后端服务..."
echo ""

# 激活虚拟环境
source venv/bin/activate

# 进入后端目录
cd backend

# 启动服务
python3 main.py
