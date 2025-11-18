#!/bin/bash
# Homebrew 和 Node.js 安装脚本
# 需要用户在终端手动运行

echo "═══════════════════════════════════════════════════════════"
echo "  安装 Homebrew 和 Node.js"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "⚠️  注意事项："
echo "  1. 需要管理员密码"
echo "  2. 安装 Homebrew 需要 5-15 分钟"
echo "  3. 安装 Node.js 需要 3-10 分钟"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# 检查是否已安装 Homebrew
if command -v brew &> /dev/null; then
    echo "✅ Homebrew 已安装"
else
    echo "📦 正在安装 Homebrew..."
    echo "   需要输入管理员密码"
    echo ""
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 配置 PATH
    echo ""
    echo "配置 Homebrew PATH..."
    
    # 检测是 Intel 还是 Apple Silicon
    if [[ $(uname -m) == 'arm64' ]]; then
        BREW_PATH="/opt/homebrew/bin/brew"
    else
        BREW_PATH="/usr/local/bin/brew"
    fi
    
    echo 'eval "$('"$BREW_PATH"' shellenv)"' >> ~/.zshrc
    eval "$($BREW_PATH shellenv)"
    
    echo "✅ Homebrew 安装完成"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

# 检查是否已安装 Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js 已安装"
    node --version
else
    echo "📦 正在安装 Node.js..."
    brew install node
    echo "✅ Node.js 安装完成"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 验证安装："
echo ""

# 验证安装
if command -v brew &> /dev/null; then
    echo "✅ Homebrew: $(brew --version | head -n 1)"
else
    echo "❌ Homebrew: 未安装"
fi

if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
    echo "✅ npm: $(npm --version)"
else
    echo "❌ Node.js: 未安装"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# 检查是否所有工具都安装成功
if command -v brew &> /dev/null && command -v node &> /dev/null; then
    echo "🎉 安装完成！"
    echo ""
    echo "下一步操作："
    echo ""
    echo "  cd /Users/feilubi/Documents/GitHub/6016b/frontend"
    echo "  npm install"
    echo "  npm run dev"
    echo ""
else
    echo "⚠️  安装未完全成功，请检查上面的错误信息"
fi

echo "═══════════════════════════════════════════════════════════"
