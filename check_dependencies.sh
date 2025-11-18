#!/bin/bash
# 依赖检查脚本

echo "==================================="
echo "    项目依赖检查工具"
echo "==================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        VERSION=$($1 --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓ $1${NC}: $VERSION"
        return 0
    else
        echo -e "${RED}✗ $1${NC}: 未安装"
        return 1
    fi
}

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓ $2${NC}"
        return 0
    else
        echo -e "${RED}✗ $2${NC}: 未安装"
        return 1
    fi
}

# 检查系统工具
echo "=== 系统环境 ==="
check_command "python3" || MISSING_PYTHON=true
check_command "pip3" || MISSING_PIP=true
check_command "node" || MISSING_NODE=true
check_command "npm" || MISSING_NPM=true

# 检查 Xcode Command Line Tools
echo ""
echo "=== 开发工具 ==="
if xcode-select -p &>/dev/null; then
    echo -e "${GREEN}✓ Xcode Command Line Tools${NC}: 已安装"
else
    echo -e "${RED}✗ Xcode Command Line Tools${NC}: 未安装"
    echo "  请运行: xcode-select --install"
    MISSING_XCODE=true
fi

# 检查 Homebrew
if command -v brew &> /dev/null; then
    BREW_VERSION=$(brew --version | head -n 1)
    echo -e "${GREEN}✓ Homebrew${NC}: $BREW_VERSION"
else
    echo -e "${YELLOW}⚠ Homebrew${NC}: 未安装（可选但推荐）"
fi

echo ""
echo "=== 后端 Python 依赖 ==="

cd backend 2>/dev/null || { echo "找不到 backend 目录"; exit 1; }

check_python_package "fastapi" "FastAPI"
check_python_package "uvicorn" "Uvicorn"
check_python_package "fitz" "PyMuPDF"
check_python_package "pdfplumber" "pdfplumber"
check_python_package "camelot" "Camelot"
check_python_package "cv2" "OpenCV"
check_python_package "yaml" "PyYAML"
check_python_package "pandas" "Pandas"
check_python_package "numpy" "NumPy"
check_python_package "mysql" "MySQL Connector"

cd ..

echo ""
echo "=== 前端 Node.js 依赖 ==="

if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓ node_modules${NC}: 已安装"
    
    if [ -d "frontend/node_modules/react" ]; then
        echo -e "${GREEN}✓ React${NC}"
    else
        echo -e "${RED}✗ React${NC}: 未安装"
    fi
    
    if [ -d "frontend/node_modules/vite" ]; then
        echo -e "${GREEN}✓ Vite${NC}"
    else
        echo -e "${RED}✗ Vite${NC}: 未安装"
    fi
    
    if [ -d "frontend/node_modules/tailwindcss" ]; then
        echo -e "${GREEN}✓ Tailwind CSS${NC}"
    else
        echo -e "${RED}✗ Tailwind CSS${NC}: 未安装"
    fi
else
    echo -e "${RED}✗ node_modules${NC}: 未安装"
    echo "  请运行: cd frontend && npm install"
    MISSING_FRONTEND=true
fi

# 检查论文模板依赖
echo ""
echo "=== 论文模板依赖 ==="

check_python_package "matplotlib" "Matplotlib"
check_python_package "requests" "Requests"

if command -v pdflatex &> /dev/null; then
    echo -e "${GREEN}✓ LaTeX${NC}: 已安装"
else
    echo -e "${YELLOW}⚠ LaTeX${NC}: 未安装（可选）"
fi

if command -v plantuml &> /dev/null; then
    echo -e "${GREEN}✓ PlantUML${NC}: 已安装"
else
    echo -e "${YELLOW}⚠ PlantUML${NC}: 未安装（可选）"
fi

if command -v dot &> /dev/null; then
    echo -e "${GREEN}✓ Graphviz${NC}: 已安装"
else
    echo -e "${YELLOW}⚠ Graphviz${NC}: 未安装（可选）"
fi

# 总结
echo ""
echo "==================================="
echo "           检查总结"
echo "==================================="

if [ -z "$MISSING_PYTHON" ] && [ -z "$MISSING_PIP" ] && [ -z "$MISSING_NODE" ] && [ -z "$MISSING_NPM" ] && [ -z "$MISSING_XCODE" ]; then
    if [ -z "$MISSING_FRONTEND" ]; then
        echo -e "${GREEN}✓ 所有必需依赖已安装！${NC}"
        echo ""
        echo "可以运行以下命令启动项目："
        echo "  后端: cd backend && python3 main.py"
        echo "  前端: cd frontend && npm run dev"
    else
        echo -e "${YELLOW}⚠ 系统环境已就绪，但需要安装依赖${NC}"
        echo ""
        echo "请运行："
        echo "  后端: pip3 install -r backend/requirements.txt"
        echo "  前端: cd frontend && npm install"
    fi
else
    echo -e "${RED}✗ 缺少必需的开发环境${NC}"
    echo ""
    echo "请先安装："
    [ -n "$MISSING_XCODE" ] && echo "  1. Xcode Command Line Tools: xcode-select --install"
    [ -n "$MISSING_PYTHON" ] && echo "  2. Python 3.x"
    [ -n "$MISSING_NODE" ] && echo "  3. Node.js"
    echo ""
    echo "详细安装说明请查看: 依赖安装指南.md"
fi

echo ""
echo "==================================="
