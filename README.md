# 大乔工具运营数据管理台

一个基于 Vue.js + Spring Boot + FastAPI 的全栈数据管理平台。

## 📋 项目架构

```
前端 (Vue.js) → 中间层 (Spring Boot) → 后端 (FastAPI)
   :8080            :9000                  :8000
```

## 🚀 快速启动

### 一键启动所有服务

```bash
./start-all.sh
```

启动后可访问：
- 前端页面: http://localhost:8080
- 后端API文档: http://localhost:8000/docs
- 中间层健康检查: http://localhost:9000/api/health

### 停止所有服务

```bash
./stop-all.sh
```

### 查看服务状态

```bash
./status.sh
```

## 📦 环境要求

- **Python**: 3.8+
- **Node.js**: 14+
- **Java**: 8+
- **Maven**: 3.6+

## 📁 项目结构

```
dqadeagent/
├── backend/              # Python FastAPI 后端
│   ├── main.py          # 后端入口
│   ├── requirements.txt # Python依赖
│   └── venv/            # Python虚拟环境
├── middle/              # Java Spring Boot 中间层
│   ├── pom.xml          # Maven配置
│   └── src/             # Java源码
├── frontend/            # Vue.js 前端
│   ├── package.json     # Node依赖
│   └── src/             # Vue源码
├── start-all.sh         # 统一启动脚本
├── stop-all.sh          # 统一停止脚本
└── status.sh            # 状态检查脚本
```

## 🔧 手动启动（可选）

### 1. 启动后端 (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### 2. 启动中间层 (Spring Boot)

```bash
cd middle
mvn clean package -DskipTests
java -jar target/middle-1.0.0.jar
```

### 3. 启动前端 (Vue.js)

```bash
cd frontend
npm install
npm run serve
```

## 📝 日志文件

各服务的日志文件位于对应目录：
- 后端: `backend/backend_service.log`
- 中间层: `middle/middle_service.log`
- 前端: `frontend/frontend_service.log`

## 🛠️ 开发说明

### 后端开发
- 框架: FastAPI
- 数据库: MySQL (通过 SQLAlchemy)
- API文档: 自动生成 (访问 /docs)

### 中间层开发
- 框架: Spring Boot 2.x
- 构建工具: Maven
- Java版本: 8

### 前端开发
- 框架: Vue 3
- UI组件: Element Plus
- 图表: ECharts
- 路由: Vue Router

## ⚠️ 常见问题

### 端口被占用
如果端口被占用，可以使用以下命令查看：
```bash
lsof -i :8000  # 后端
lsof -i :9000  # 中间层
lsof -i :8080  # 前端
```

### 服务启动失败
1. 检查环境是否满足要求
2. 查看对应的日志文件
3. 确保依赖已正确安装

### Node.js 版本兼容性
如果使用 Node.js v23+，可能会遇到兼容性问题，建议使用 LTS 版本（v20 或 v22）。

## 📄 许可证

内部项目
