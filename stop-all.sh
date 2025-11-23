#!/bin/bash

# 大乔工具运营数据管理台 - 统一停止脚本
# 作者: DQA DE Agent Team
# 说明: 一键停止所有服务（后端、中间层、前端）

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
echo "🛑 大乔工具运营数据管理台 - 停止脚本"
echo -e "==========================================${NC}"
echo ""

# 读取PID文件
if [ -f "service.pid" ]; then
    source service.pid
    
    # 停止后端
    if [ ! -z "$BACKEND_PID" ]; then
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}🛑 停止后端服务 (PID: $BACKEND_PID)...${NC}"
            kill $BACKEND_PID 2>/dev/null
            echo -e "${GREEN}✅ 后端服务已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
        fi
    fi
    
    # 停止中间层
    if [ ! -z "$MIDDLE_PID" ]; then
        if ps -p $MIDDLE_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}🛑 停止中间层服务 (PID: $MIDDLE_PID)...${NC}"
            kill $MIDDLE_PID 2>/dev/null
            echo -e "${GREEN}✅ 中间层服务已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  中间层服务未运行${NC}"
        fi
    fi
    
    # 停止前端
    if [ ! -z "$FRONTEND_PID" ]; then
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}🛑 停止前端服务 (PID: $FRONTEND_PID)...${NC}"
            kill $FRONTEND_PID 2>/dev/null
            # 同时停止相关的node进程
            pkill -P $FRONTEND_PID 2>/dev/null
            echo -e "${GREEN}✅ 前端服务已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
        fi
    fi
    
    # 删除PID文件
    rm -f service.pid
else
    echo -e "${YELLOW}⚠️  未找到PID文件，尝试按端口停止服务...${NC}"
    
    # 按端口停止服务
    echo -e "${YELLOW}🛑 停止8000端口服务 (后端)...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✅ 后端服务已停止${NC}" || echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
    
    echo -e "${YELLOW}🛑 停止9000端口服务 (中间层)...${NC}"
    lsof -ti:9000 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✅ 中间层服务已停止${NC}" || echo -e "${YELLOW}⚠️  中间层服务未运行${NC}"
    
    echo -e "${YELLOW}🛑 停止8080端口服务 (前端)...${NC}"
    lsof -ti:8080 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✅ 前端服务已停止${NC}" || echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
fi

# 清理各服务目录的PID文件
rm -f "$SCRIPT_DIR/backend/service.pid" 2>/dev/null
rm -f "$SCRIPT_DIR/middle/service.pid" 2>/dev/null
rm -f "$SCRIPT_DIR/frontend/service.pid" 2>/dev/null

echo ""
echo -e "${BLUE}=========================================="
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${BLUE}==========================================${NC}"

