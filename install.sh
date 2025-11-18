#!/bin/bash
# 一键安装脚本

set -e  # 遇到错误立即退出

echo "========================================="
echo "   6016b 项目依赖安装脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 错误处理
error_exit() {
    echo -e "${RED}错误: $1${NC}" >&2
    exit 1
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

# 步骤1: 检查基本环境
echo "步骤 1/6: 检查基本环境..."

if ! check_command python3; then
    error_exit "Python 3 未安装。请先安装 Python 3.x"
fi
echo -e "${GREEN}✓ Python 3 已安装${NC}"

if ! check_command pip3; then
    error_exit "pip3 未安装。请先安装 pip"
fi
echo -e "${GREEN}✓ pip3 已安装${NC}"

if ! check_command node; then
    echo -e "${YELLOW}⚠ Node.js 未安装${NC}"
    echo "  前端功能将无法使用"
    INSTALL_FRONTEND=false
else
    echo -e "${GREEN}✓ Node.js 已安装${NC}"
    INSTALL_FRONTEND=true
fi

# 检查 Xcode Command Line Tools
if ! xcode-select -p &>/dev/null; then
    echo -e "${RED}✗ Xcode Command Line Tools 未安装${NC}"
    echo "  请运行: xcode-select --install"
    error_exit "需要先安装 Xcode Command Line Tools"
fi
echo -e "${GREEN}✓ Xcode Command Line Tools 已安装${NC}"

echo ""

# 步骤2: 升级 pip
echo "步骤 2/6: 升级 pip..."
python3 -m pip install --upgrade pip --user
echo -e "${GREEN}✓ pip 已升级${NC}"
echo ""

# 步骤3: 创建虚拟环境（推荐）
echo "步骤 3/6: 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
else
    echo -e "${YELLOW}⚠ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 步骤4: 安装后端依赖
echo "步骤 4/6: 安装后端 Python 依赖..."

# 检查是否有requirements.txt
if [ ! -f "backend/requirements.txt" ]; then
    error_exit "找不到 backend/requirements.txt"
fi

echo "正在安装 Python 包..."
pip install -r backend/requirements.txt

# 如果失败，尝试逐个安装关键包
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ 批量安装失败，尝试逐个安装关键包${NC}"
    
    pip install fastapi uvicorn python-dotenv mysql-connector-python
    pip install PyMuPDF pdfplumber PyYAML numpy pandas requests
    
    echo -e "${YELLOW}⚠ 部分可选包可能需要手动安装${NC}"
fi

echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
echo ""

# 步骤5: 安装前端依赖
if [ "$INSTALL_FRONTEND" = true ]; then
    echo "步骤 5/6: 安装前端 Node.js 依赖..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # 检查package.json
        if [ ! -f "package.json" ]; then
            echo -e "${YELLOW}⚠ 找不到 frontend/package.json${NC}"
        else
            # 检查node_modules是否存在
            if [ ! -d "node_modules" ]; then
                echo "正在安装 npm 包..."
                npm install
                
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
                else
                    echo -e "${YELLOW}⚠ npm 安装出现警告，但可能可以正常运行${NC}"
                fi
            else
                echo -e "${YELLOW}⚠ node_modules 已存在，跳过安装${NC}"
                echo "  如需重新安装，请运行: cd frontend && rm -rf node_modules && npm install"
            fi
        fi
        
        cd ..
    else
        echo -e "${YELLOW}⚠ frontend 目录不存在，跳过${NC}"
    fi
    echo ""
else
    echo "步骤 5/6: 跳过前端依赖安装（Node.js 未安装）"
    echo ""
fi

# 步骤6: 验证安装
echo "步骤 6/6: 验证安装..."

echo ""
echo "验证 Python 包..."
python3 << 'PYTHON_EOF'
import sys
packages = [
    'fastapi', 'uvicorn', 'fitz', 'pdfplumber', 
    'camelot', 'yaml', 'pandas', 'numpy', 'requests'
]

success_count = 0
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg}")
        success_count += 1
    except ImportError:
        print(f"✗ {pkg} - 未安装")

if success_count == len(packages):
    print(f"\n✓ 所有关键包已安装 ({success_count}/{len(packages)})")
    sys.exit(0)
else:
    print(f"\n⚠ 部分包未安装 ({success_count}/{len(packages)})")
    sys.exit(1)
PYTHON_EOF

echo ""
echo "========================================="
echo "           安装完成！"
echo "========================================="
echo ""

echo -e "${GREEN}✓ 后端环境已就绪${NC}"
if [ "$INSTALL_FRONTEND" = true ]; then
    echo -e "${GREEN}✓ 前端环境已就绪${NC}"
fi

echo ""
echo "下一步操作："
echo ""
echo "1. 启动后端服务："
echo "   source venv/bin/activate"
echo "   cd backend && python3 main.py"
echo ""
if [ "$INSTALL_FRONTEND" = true ]; then
    echo "2. 启动前端服务（新终端）："
    echo "   cd frontend && npm run dev"
    echo ""
fi
echo "3. 访问应用："
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo ""
echo "4. 运行依赖检查："
echo "   ./check_dependencies.sh"
echo ""
echo "========================================="
