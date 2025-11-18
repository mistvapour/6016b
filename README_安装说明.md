# 6016b 项目 - 安装说明

## 📍 当前位置

您正在查看 **6016b** 项目的依赖安装说明。

---

## ⚠️ 重要提示

您的系统检测到以下状态：

```
❌ Xcode Command Line Tools - 未安装（必需）
❌ Node.js - 未安装
⚠️ Python - 需要 Xcode 工具支持
```

**必须先安装 Xcode Command Line Tools 才能继续！**

---

## 🚀 立即开始（3 步）

### 第 1 步：安装 Xcode 开发工具 ⏰ 10-30分钟

打开终端，运行：

```bash
xcode-select --install
```

**按照对话框提示操作！**

---

### 第 2 步：运行项目安装 ⏰ 5-15分钟

Xcode 工具安装完成后：

```bash
cd /Users/feilubi/Documents/GitHub/6016b
./install.sh
```

---

### 第 3 步：验证安装 ⏰ 1分钟

```bash
./check_dependencies.sh
```

应该看到所有 ✓ 绿色标记！

---

## 📂 项目结构

```
6016b/
├── backend/              # Python 后端服务
├── frontend/             # React 前端应用  
├── 论文模板/             # LaTeX 文档
├── install.sh           # ⭐ 一键安装脚本
├── check_dependencies.sh # ⭐ 依赖检查
├── INSTALL.md           # ⭐ 安装指南
└── 快速开始.md           # ⭐ 快速入门
```

---

## 📚 文档导航

### 快速入门
- **下一步操作.txt** ← 👈 从这里开始！
- **快速开始.md** - 3 分钟了解安装流程

### 详细文档
- **INSTALL.md** - 完整安装指南（推荐）
- **依赖安装指南.md** - 详细步骤说明
- **项目结构说明.md** - 项目概览

### 参考文档
- **功能需求检查报告.md** - 功能分析
- **功能检查摘要.md** - 功能概览

---

## 🎯 安装流程图

```
开始
  ↓
第1步: 安装 Xcode Command Line Tools
  ↓         (10-30分钟)
  ✓ Xcode 安装完成
  ↓
第2步: 运行 ./install.sh
  ↓         (5-15分钟)
  ✓ 依赖安装完成
  ↓
第3步: 运行 ./check_dependencies.sh
  ↓         (1分钟)
  ✓ 验证通过
  ↓
完成！可以启动项目了 🎉
```

---

## 🔍 常见问题

### Q: 为什么要安装 Xcode Command Line Tools？
A: 这是 macOS 上所有开发工具的基础，包括编译器和开发库。

### Q: 安装 Xcode 需要多长时间？
A: 一般 10-30 分钟，取决于网络速度。

### Q: 我可以用 GitHub Desktop 吗？
A: 可以，但 Git 命令行仍然建议安装 Xcode 工具。

### Q: 安装脚本会做什么？
A: 自动检查环境、创建虚拟环境、安装 Python 和 Node.js 依赖。

---

## 💡 提示

1. **首次安装**: 建议按照 `下一步操作.txt` 逐步操作
2. **遇到问题**: 查看 `INSTALL.md` 的故障排除部分
3. **需要帮助**: 提供错误信息到项目 Issues

---

## ✅ 验证清单

安装完成后，应该能够：

- [ ] 运行 `./check_dependencies.sh` 无错误
- [ ] 启动后端：`cd backend && python3 main.py`
- [ ] 启动前端：`cd frontend && npm run dev`
- [ ] 访问 http://localhost:8000（后端）
- [ ] 访问 http://localhost:5173（前端）

---

## 📞 获取帮助

如果在安装过程中遇到问题：

1. 查看 **INSTALL.md** 中的故障排除部分
2. 运行 **check_dependencies.sh** 查看详细状态
3. 提供以下信息：
   - 操作系统版本：`sw_vers`
   - Python 版本：`python3 --version`  
   - 错误日志

---

## 🎉 准备好了吗？

现在就打开终端，运行：

```bash
xcode-select --install
```

然后等待安装完成！

---

**项目路径**: /Users/feilubi/Documents/GitHub/6016b  
**更新时间**: 2024-01-XX
