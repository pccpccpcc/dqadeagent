#!/bin/bash

# 大乔工具运营数据管理台 - 前端启动脚本
# 作者: DQA DE Agent Team
# 说明: 启动前端服务 (Vue.js)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}=========================================="
echo "🚀 启动前端服务 (Vue.js)"
echo -e "==========================================${NC}"
echo ""

# 检查Node.js环境
echo -e "${YELLOW}[1/3] 检查Node.js环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装，请先安装 Node.js 14+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js环境检查通过${NC}"
echo "  - Node.js: $(node --version)"
echo "  - NPM: $(npm --version)"
echo ""

# 进入前端目录
cd "$SCRIPT_DIR/frontend"

# 检查依赖
echo -e "${YELLOW}[2/3] 准备前端依赖...${NC}"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 安装前端依赖...${NC}"
    npm install
fi
echo -e "${GREEN}✅ 前端依赖准备完成${NC}"
echo ""

# 启动前端
echo -e "${YELLOW}[3/3] 启动前端服务...${NC}"
echo -e "${GREEN}🚀 启动前端服务 (端口: 8080)...${NC}"
nohup npm run serve > frontend_service.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > service.pid

# 等待前端启动
sleep 8

# 检查服务是否启动成功
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
    echo ""
    echo -e "${BLUE}=========================================="
    echo "✅ 前端服务启动完成！"
    echo -e "==========================================${NC}"
    echo ""
    echo -e "${GREEN}🎯 服务信息：${NC}"
    echo -e "  📱 前端页面:   ${BLUE}http://localhost:8080${NC}"
    echo ""
    echo -e "${GREEN}📝 进程信息：${NC}"
    echo "  PID: $FRONTEND_PID"
    echo "  日志: frontend/frontend_service.log"
    echo ""
    echo -e "${YELLOW}💡 提示：${NC}"
    echo "  - 使用 ${GREEN}./stop-all.sh${NC} 停止服务"
    echo "  - 使用 ${GREEN}./status.sh${NC} 查看服务状态"
    echo -e "${BLUE}==========================================${NC}"
else
    echo -e "${RED}❌ 前端服务启动失败${NC}"
    echo "请查看日志: frontend/frontend_service.log"
    exit 1
fi






