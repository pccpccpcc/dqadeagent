#!/bin/bash

# 大乔工具运营数据管理台 - 统一启动脚本
# 作者: DQA DE Agent Team
# 说明: 一键启动所有服务（后端、中间层、前端）

set -e  # 遇到错误立即退出

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
echo "🚀 大乔工具运营数据管理台 - 启动脚本"
echo -e "==========================================${NC}"
echo ""

# 检查环境
echo -e "${YELLOW}[1/4] 检查运行环境...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装，请先安装 Python 3.8+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装，请先安装 Node.js 14+${NC}"
    exit 1
fi

if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java 未安装，请先安装 Java 8+${NC}"
    exit 1
fi

if ! command -v mvn &> /dev/null; then
    echo -e "${RED}❌ Maven 未安装，请先安装 Maven${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"
echo "  - Python: $(python3 --version)"
echo "  - Node.js: $(node --version)"
echo "  - Java: $(java -version 2>&1 | head -n 1)"
echo "  - Maven: $(mvn --version | head -n 1)"
echo ""

# 启动后端服务
echo -e "${YELLOW}[2/4] 启动后端服务 (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 创建Python虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
if [ ! -f "venv/.dependencies_installed" ]; then
    echo -e "${YELLOW}📦 安装后端依赖...${NC}"
    pip install -q -r requirements.txt
    touch venv/.dependencies_installed
fi

# 启动后端
echo -e "${GREEN}🚀 启动后端服务 (端口: 8000)...${NC}"
nohup python3 app.py > backend_service.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > service.pid
echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
echo -e "${YELLOW}⏳ 等待后端服务就绪...${NC}"
sleep 3

# 启动中间层服务
echo ""
echo -e "${YELLOW}[3/4] 启动中间层服务 (Spring Boot)...${NC}"
cd "$SCRIPT_DIR/middle"

# 检查JAR包是否存在
if [ ! -f "target/middle-1.0.0.jar" ]; then
    echo -e "${YELLOW}📦 编译中间层项目...${NC}"
    mvn clean package -DskipTests -q
fi

# 启动中间层
echo -e "${GREEN}🚀 启动中间层服务 (端口: 9000)...${NC}"
nohup java -jar target/middle-1.0.0.jar > middle_service.log 2>&1 &
MIDDLE_PID=$!
echo $MIDDLE_PID > service.pid
echo -e "${GREEN}✅ 中间层服务已启动 (PID: $MIDDLE_PID)${NC}"

# 等待中间层启动
echo -e "${YELLOW}⏳ 等待中间层服务就绪...${NC}"
sleep 5

# 启动前端服务
echo ""
echo -e "${YELLOW}[4/4] 启动前端服务 (Vue.js)...${NC}"
cd "$SCRIPT_DIR/frontend"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 安装前端依赖...${NC}"
    npm install
fi

# 启动前端
echo -e "${GREEN}🚀 启动前端服务 (端口: 8080)...${NC}"
nohup npm run serve > frontend_service.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > service.pid
echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"

# 等待前端启动
echo -e "${YELLOW}⏳ 等待前端服务就绪...${NC}"
sleep 8

# 保存所有PID到根目录
cd "$SCRIPT_DIR"
cat > service.pid << EOF
BACKEND_PID=$BACKEND_PID
MIDDLE_PID=$MIDDLE_PID
FRONTEND_PID=$FRONTEND_PID
EOF

# 显示启动结果
echo ""
echo -e "${BLUE}=========================================="
echo "✅ 全部服务启动完成！"
echo -e "==========================================${NC}"
echo ""
echo -e "${GREEN}🎯 服务信息：${NC}"
echo -e "  📱 前端 (Vue.js):     ${BLUE}http://localhost:8080${NC}"
echo -e "  🔗 中间层 (Spring):   ${BLUE}http://localhost:9000${NC}"
echo -e "  📡 后端 (FastAPI):    ${BLUE}http://localhost:8000${NC}"
echo ""
echo -e "${GREEN}🔄 调用链路：${NC}"
echo "  前端 → 中间层 → 后端"
echo ""
echo -e "${GREEN}📚 接口文档：${NC}"
echo -e "  后端API文档:          ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  中间层健康检查:       ${BLUE}http://localhost:9000/api/health${NC}"
echo ""
echo -e "${GREEN}📝 进程信息：${NC}"
echo "  后端PID:   $BACKEND_PID"
echo "  中间层PID: $MIDDLE_PID"
echo "  前端PID:   $FRONTEND_PID"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "  - 使用 ${GREEN}./stop-all.sh${NC} 停止所有服务"
echo "  - 使用 ${GREEN}./status.sh${NC} 查看服务状态"
echo "  - 日志文件位于各服务目录的 *_service.log"
echo -e "${BLUE}==========================================${NC}"

