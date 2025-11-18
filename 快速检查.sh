#!/bin/bash

echo "检查 Node.js 和 npm..."
echo ""

# 检查当前 shell 的 PATH
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
    echo "   路径: $(which node)"
else
    echo "❌ Node.js: 未找到"
    echo ""
    echo "可能的路径："
    ls -la /usr/local/bin/node 2>/dev/null && echo "/usr/local/bin/node 存在"
    ls -la /opt/homebrew/bin/node 2>/dev/null && echo "/opt/homebrew/bin/node 存在"
fi

echo ""

if command -v npm &> /dev/null; then
    echo "✅ npm: $(npm --version)"
    echo "   路径: $(which npm)"
else
    echo "❌ npm: 未找到"
    echo ""
    echo "可能的路径："
    ls -la /usr/local/bin/npm 2>/dev/null && echo "/usr/local/bin/npm 存在"
    ls -la /opt/homebrew/bin/npm 2>/dev/null && echo "/opt/homebrew/bin/npm 存在"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "完整 PATH："
echo $PATH | tr ':' '\n' | nl
