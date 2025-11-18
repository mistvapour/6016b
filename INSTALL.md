# 安装指南

## ⚡ 快速安装（5分钟）

### 前置要求

✅ macOS 系统  
✅ 已安装 Xcode Command Line Tools

### 一键安装

```bash
# 1. 克隆或进入项目目录
cd /Users/feilubi/Documents/GitHub/6016b

# 2. 运行安装脚本
./install.sh

# 3. 运行依赖检查
./check_dependencies.sh
```

### 如果 Xcode Command Line Tools 未安装

```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 等待安装完成（10-30分钟），然后重新运行
./install.sh
```

---

## 📋 完整安装流程

### 步骤 1: 安装系统依赖

#### macOS 必需工具

```bash
# 安装 Xcode Command Line Tools
xcode-select --install
```

#### 可选但推荐：Homebrew

```bash
# 安装 Homebrew 包管理器
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 添加到 PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

---

### 步骤 2: 安装 Python 环境

#### 使用 Homebrew 安装

```bash
brew install python@3.11
```

#### 或下载官方安装包

访问 https://www.python.org/downloads/ 下载安装

#### 验证

```bash
python3 --version  # 应该显示 Python 3.x.x
pip3 --version     # 应该显示 pip 版本
```

---

### 步骤 3: 安装 Node.js

#### 使用 Homebrew 安装

```bash
brew install node
```

#### 或下载官方安装包

访问 https://nodejs.org/ 下载 LTS 版本

#### 验证

```bash
node --version  # 应该显示 v20.x.x
npm --version   # 应该显示版本号
```

---

### 步骤 4: 安装项目依赖

#### 后端依赖

```bash
# 进入项目目录
cd /Users/feilubi/Documents/GitHub/6016b

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt
```

#### 前端依赖

```bash
cd frontend
npm install
cd ..
```

#### 论文模板依赖（可选）

```bash
# 安装 LaTeX
brew install --cask mactex

# 安装 Python 工具
pip install matplotlib plantuml requests
```

---

### 步骤 5: 验证安装

```bash
# 运行检查脚本
./check_dependencies.sh

# 应该看到所有 ✓ 标记
```

---

## 🚀 启动项目

### 启动后端

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务
cd backend
python3 main.py
```

后端将在 http://localhost:8000 启动

### 启动前端

```bash
# 在新终端窗口
cd frontend
npm run dev
```

前端将在 http://localhost:5173 启动

---

## 🐛 故障排除

### 问题 1: pip 安装失败

**症状**: `pip install` 报错或超时

**解决**:
```bash
# 升级 pip
python3 -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r backend/requirements.txt
```

---

### 问题 2: OpenCV 安装失败

**症状**: `opencv-python` 无法安装

**解决**:
```bash
# 先安装系统依赖
brew install opencv

# 再安装 Python 包
pip install opencv-python
```

---

### 问题 3: Camelot 安装失败

**症状**: `camelot-py` 安装失败

**解决**:
```bash
# 安装系统依赖
brew install ghostscript imagemagick

# 安装 Python 包
pip install camelot-py[cv]
```

---

### 问题 4: npm 安装慢

**症状**: `npm install` 非常慢或超时

**解决**:
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 清除缓存重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### 问题 5: Xcode Command Line Tools 错误

**症状**: `xcrun: error: invalid active developer path`

**解决**:
```bash
# 重新安装
sudo xcode-select --install

# 或重置路径
sudo xcode-select --reset
```

---

## 📊 依赖概览

### Python 包

- **核心框架**: FastAPI, Uvicorn
- **PDF处理**: PyMuPDF, pdfplumber, camelot
- **数据处理**: pandas, numpy
- **图像处理**: OpenCV, Pillow
- **配置**: PyYAML, python-dotenv

### Node.js 包

- **框架**: React 19, Vite
- **UI组件**: Radix UI
- **样式**: Tailwind CSS
- **图标**: Lucide React
- **图表**: Recharts

---

## ✅ 安装检查清单

使用以下命令逐一检查：

```bash
# 1. 系统工具
xcode-select -p && echo "✓ Xcode CLI Tools"

# 2. Python
python3 --version && echo "✓ Python"
pip3 --version && echo "✓ pip"

# 3. Node.js
node --version && echo "✓ Node.js"
npm --version && echo "✓ npm"

# 4. Python 包
python3 -c "import fastapi, fitz, pdfplumber; print('✓ 核心包')"

# 5. Node.js 包
cd frontend && npm list react vite 2>/dev/null && echo "✓ 前端包"

# 6. 运行检查脚本
cd .. && ./check_dependencies.sh
```

---

## 📚 更多文档

- **详细安装指南**: `依赖安装指南.md`
- **项目结构说明**: `项目结构说明.md`
- **功能检查报告**: `功能需求检查报告.md`
- **系统架构**: `SYSTEM_ARCHITECTURE_OVERVIEW.md`

---

## 💡 提示

1. **虚拟环境**: 强烈建议使用 Python 虚拟环境避免依赖冲突
2. **镜像加速**: 在中国大陆建议使用镜像加速安装
3. **分步安装**: 如果一键安装失败，可以按步骤手动安装
4. **查看日志**: 安装过程中的错误信息通常会提供解决线索

---

**需要帮助？**

如果遇到其他问题，请提供：
- 错误日志
- 操作系统版本: `sw_vers`
- Python 版本: `python3 --version`
- Node.js 版本: `node --version`
