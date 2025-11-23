#!/bin/bash

# 大乔工具运营数据管理台 - 服务状态检查脚本
# 作者: DQA DE Agent Team
# 说明: 查看所有服务的运行状态

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
echo "📊 大乔工具运营数据管理台 - 服务状态"
echo -e "==========================================${NC}"
echo ""

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        local pid=$(lsof -ti:$port)
        echo -e "${GREEN}✅ $service_name${NC} - 运行中 (端口: $port, PID: $pid)"
        return 0
    else
        echo -e "${RED}❌ $service_name${NC} - 未运行 (端口: $port)"
        return 1
    fi
}

# 检查各服务状态
echo -e "${YELLOW}服务状态：${NC}"
check_port 8000 "后端服务 (FastAPI)   "
BACKEND_STATUS=$?

check_port 9000 "中间层服务 (Spring)  "
MIDDLE_STATUS=$?

check_port 8080 "前端服务 (Vue.js)    "
FRONTEND_STATUS=$?

echo ""

# 显示服务URL
if [ $BACKEND_STATUS -eq 0 ] || [ $MIDDLE_STATUS -eq 0 ] || [ $FRONTEND_STATUS -eq 0 ]; then
    echo -e "${YELLOW}服务地址：${NC}"
    [ $FRONTEND_STATUS -eq 0 ] && echo -e "  📱 前端:     ${BLUE}http://localhost:8080${NC}"
    [ $MIDDLE_STATUS -eq 0 ] && echo -e "  🔗 中间层:   ${BLUE}http://localhost:9000${NC}"
    [ $BACKEND_STATUS -eq 0 ] && echo -e "  📡 后端:     ${BLUE}http://localhost:8000${NC}"
    [ $BACKEND_STATUS -eq 0 ] && echo -e "  📚 API文档:  ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
fi

# 显示PID信息
if [ -f "service.pid" ]; then
    echo -e "${YELLOW}PID信息：${NC}"
    cat service.pid
    echo ""
fi

# 总结
echo -e "${BLUE}==========================================${NC}"
if [ $BACKEND_STATUS -eq 0 ] && [ $MIDDLE_STATUS -eq 0 ] && [ $FRONTEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有服务运行正常${NC}"
elif [ $BACKEND_STATUS -ne 0 ] && [ $MIDDLE_STATUS -ne 0 ] && [ $FRONTEND_STATUS -ne 0 ]; then
    echo -e "${RED}❌ 所有服务未运行${NC}"
    echo -e "${YELLOW}💡 使用 ./start-all.sh 启动服务${NC}"
else
    echo -e "${YELLOW}⚠️  部分服务未运行${NC}"
    echo -e "${YELLOW}💡 使用 ./start-all.sh 启动所有服务${NC}"
fi
echo -e "${BLUE}==========================================${NC}"

