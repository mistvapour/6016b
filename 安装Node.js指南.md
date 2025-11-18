# 安装 Node.js 指南

## ⚠️ 检测到的情况

您的终端显示：
```
zsh: command not found: brew
zsh: command not found: npm
```

这说明需要先安装 Homebrew，然后才能安装 Node.js。

---

## 📋 安装步骤

### 第 1 步：安装 Homebrew

在终端运行以下命令：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**这个过程需要：**
- 5-15 分钟
- 可能需要输入管理员密码
- 需要确认操作

---

### 第 2 步：配置 Homebrew

安装完成后，会看到提示信息，类似：

```
Next steps:
- Run these commands in your terminal to add Homebrew to your PATH
```

按照提示运行命令，通常是：

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
```

---

### 第 3 步：验证 Homebrew

```bash
brew --version
```

应该显示 Homebrew 版本号。

---

### 第 4 步：安装 Node.js

```bash
brew install node
```

---

### 第 5 步：验证 Node.js

```bash
node --version
npm --version
```

---

### 第 6 步：安装前端依赖

```bash
cd /Users/feilubi/Documents/GitHub/6016b/frontend
npm install
```

---

### 第 7 步：启动前端

```bash
npm run dev
```

---

## 🚀 快速安装（推荐）

复制粘贴以下完整命令序列：

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 配置 PATH（按照提示运行相应命令）
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"

# 验证
brew --version

# 安装 Node.js
brew install node

# 验证 Node.js
node --version
npm --version

# 进入前端目录
cd /Users/feilubi/Documents/GitHub/6016b/frontend

# 安装依赖
npm install

# 启动前端
npm run dev
```

---

## ⏱️ 预计时间

- **Homebrew 安装**: 5-15 分钟
- **Node.js 安装**: 3-10 分钟
- **前端依赖**: 2-5 分钟

**总计**: 约 10-30 分钟

---

## 🔄 替代方案

如果不想安装 Homebrew，可以直接下载 Node.js：

访问: https://nodejs.org/

下载并安装 LTS 版本，然后：

```bash
cd /Users/feilubi/Documents/GitHub/6016b/frontend
npm install
npm run dev
```

---

## ✅ 安装检查清单

- [ ] Homebrew 已安装
- [ ] Node.js 已安装
- [ ] npm 已安装
- [ ] 前端依赖已安装
- [ ] 前端可以启动

---

**准备开始了吗？在终端运行第一行命令！** 🚀
