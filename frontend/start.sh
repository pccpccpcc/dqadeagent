#!/bin/bash

cd "$(dirname "$0")"

echo "=========================================="
echo "启动Frontend服务"
echo "=========================================="

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到node"
    exit 1
fi

echo "Node版本: $(node --version)"
echo "NPM版本: $(npm --version)"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "错误: node_modules不存在，请先运行 npm install"
    exit 1
fi

echo ""
echo "启动Vue开发服务器..."
echo "服务地址: http://localhost:8080"
echo "=========================================="
echo ""

# 启动服务
exec npm run serve






