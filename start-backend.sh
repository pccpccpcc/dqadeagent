#!/bin/bash

# 大乔工具运营数据管理台 - 后端启动脚本
# 作者: DQA DE Agent Team
# 说明: 启动后端服务 (FastAPI)

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
echo "🚀 启动后端服务 (FastAPI)"
echo -e "==========================================${NC}"
echo ""

# 检查Python环境
echo -e "${YELLOW}[1/3] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装，请先安装 Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python环境检查通过${NC}"
echo "  - Python: $(python3 --version)"
echo ""

# 进入后端目录
cd "$SCRIPT_DIR/backend"

# 检查依赖
echo -e "${YELLOW}[2/3] 检查Python依赖...${NC}"
echo -e "${GREEN}✅ 跳过虚拟环境，使用系统Python${NC}"
echo ""

# 启动后端
echo -e "${YELLOW}[3/3] 启动后端服务...${NC}"
echo -e "${GREEN}🚀 启动后端服务 (端口: 8000)...${NC}"
nohup python3 app.py > backend_service.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > service.pid

# 等待后端启动
sleep 3

# 检查服务是否启动成功
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    echo ""
    echo -e "${BLUE}=========================================="
    echo "✅ 后端服务启动完成！"
    echo -e "==========================================${NC}"
    echo ""
    echo -e "${GREEN}🎯 服务信息：${NC}"
    echo -e "  📡 后端API:    ${BLUE}http://localhost:8000${NC}"
    echo -e "  📚 API文档:    ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${GREEN}📝 进程信息：${NC}"
    echo "  PID: $BACKEND_PID"
    echo "  日志: backend/backend_service.log"
    echo ""
    echo -e "${YELLOW}💡 提示：${NC}"
    echo "  - 使用 ${GREEN}./stop-all.sh${NC} 停止服务"
    echo "  - 使用 ${GREEN}./status.sh${NC} 查看服务状态"
    echo -e "${BLUE}==========================================${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo "请查看日志: backend/backend_service.log"
    exit 1
fi

