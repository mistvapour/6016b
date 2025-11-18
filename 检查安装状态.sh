#!/bin/bash
# 检查 Xcode Command Line Tools 安装状态

echo "=============================================="
echo "   检查 Xcode Command Line Tools 状态"
echo "=============================================="
echo ""

# 检查命令路径
echo "1. 检查开发者目录..."
if xcode-select -p &>/dev/null; then
    PATH_DIR=$(xcode-select -p)
    echo "   ✅ 已安装"
    echo "   路径: $PATH_DIR"
    exit 0
else
    echo "   ❌ 未安装或正在安装中"
fi

echo ""
echo "2. 检查安装包..."
if pkgutil --pkg-info=com.apple.pkg.CLTools_Executables &>/dev/null; then
    echo "   ✅ 安装包已检测到"
    pkgutil --pkg-info=com.apple.pkg.CLTools_Executables | grep "install-time"
else
    echo "   ⏳ 安装包未检测到"
fi

echo ""
echo "3. 检查系统更新状态..."
if softwareupdate --list &>/dev/null 2>&1; then
    echo "   ✅ 系统更新工具可用"
else
    echo "   ⚠️  无法检查系统更新"
fi

echo ""
echo "=============================================="
echo "              状态总结"
echo "=============================================="

if xcode-select -p &>/dev/null; then
    echo ""
    echo "✅ Xcode Command Line Tools 已安装！"
    echo ""
    echo "下一步：运行 ./install.sh"
    echo ""
else
    echo ""
    echo "⚠️  Xcode Command Line Tools 未安装"
    echo ""
    echo "请确保："
    echo "1. 已运行 xcode-select --install"
    echo "2. 已点击对话框中的 '安装' 按钮"
    echo "3. 等待 10-30 分钟完成安装"
    echo ""
    echo "验证安装后运行：./install.sh"
    echo ""
fi

echo "=============================================="
