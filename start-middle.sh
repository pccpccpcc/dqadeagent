#!/bin/bash

# 大乔工具运营数据管理台 - 中间层启动脚本
# 作者: DQA DE Agent Team
# 说明: 启动中间层服务 (Spring Boot)

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
echo "🚀 启动中间层服务 (Spring Boot)"
echo -e "==========================================${NC}"
echo ""

# 检查Java和Maven环境
echo -e "${YELLOW}[1/3] 检查Java和Maven环境...${NC}"
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java 未安装，请先安装 Java 8+${NC}"
    exit 1
fi

if ! command -v mvn &> /dev/null; then
    echo -e "${RED}❌ Maven 未安装，请先安装 Maven${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Java和Maven环境检查通过${NC}"
echo "  - Java: $(java -version 2>&1 | head -n 1)"
echo "  - Maven: $(mvn --version | head -n 1)"
echo ""

# 进入中间层目录
cd "$SCRIPT_DIR/middle"

# 检查JAR包是否存在
echo -e "${YELLOW}[2/3] 准备中间层应用...${NC}"
if [ ! -f "target/middle-1.0.0.jar" ]; then
    echo -e "${YELLOW}📦 编译中间层项目...${NC}"
    mvn clean package -DskipTests -q
fi
echo -e "${GREEN}✅ 中间层应用准备完成${NC}"
echo ""

# 启动中间层
echo -e "${YELLOW}[3/3] 启动中间层服务...${NC}"
echo -e "${GREEN}🚀 启动中间层服务 (端口: 9000)...${NC}"
nohup java -jar target/middle-1.0.0.jar > middle_service.log 2>&1 &
MIDDLE_PID=$!
echo $MIDDLE_PID > service.pid

# 等待中间层启动
sleep 5

# 检查服务是否启动成功
if ps -p $MIDDLE_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 中间层服务已启动 (PID: $MIDDLE_PID)${NC}"
    echo ""
    echo -e "${BLUE}=========================================="
    echo "✅ 中间层服务启动完成！"
    echo -e "==========================================${NC}"
    echo ""
    echo -e "${GREEN}🎯 服务信息：${NC}"
    echo -e "  🔗 中间层API:  ${BLUE}http://localhost:9000${NC}"
    echo -e "  💚 健康检查:   ${BLUE}http://localhost:9000/api/health${NC}"
    echo ""
    echo -e "${GREEN}📝 进程信息：${NC}"
    echo "  PID: $MIDDLE_PID"
    echo "  日志: middle/middle_service.log"
    echo ""
    echo -e "${YELLOW}💡 提示：${NC}"
    echo "  - 使用 ${GREEN}./stop-all.sh${NC} 停止服务"
    echo "  - 使用 ${GREEN}./status.sh${NC} 查看服务状态"
    echo -e "${BLUE}==========================================${NC}"
else
    echo -e "${RED}❌ 中间层服务启动失败${NC}"
    echo "请查看日志: middle/middle_service.log"
    exit 1
fi






