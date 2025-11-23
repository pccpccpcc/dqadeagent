# 快速开始指南

## 🎯 一分钟启动

```bash
# 1. 启动所有服务
./start-all.sh

# 2. 访问前端页面
# 打开浏览器访问: http://localhost:8080
```

就这么简单！✨

---

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `./start-all.sh` | 启动所有服务（后端+中间层+前端） |
| `./stop-all.sh` | 停止所有服务 |
| `./status.sh` | 查看服务运行状态 |

---

## 🌐 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:8080 | Vue.js 用户界面 |
| 中间层 | http://localhost:9000 | Spring Boot API |
| 后端 | http://localhost:8000 | FastAPI 数据服务 |
| API文档 | http://localhost:8000/docs | Swagger 文档 |

---

## 🔍 故障排查

### 服务启动失败？

```bash
# 1. 查看服务状态
./status.sh

# 2. 查看日志
tail -f backend/backend_service.log
tail -f middle/middle_service.log
tail -f frontend/frontend_service.log

# 3. 重启服务
./stop-all.sh
./start-all.sh
```

### 端口被占用？

```bash
# 查看端口占用
lsof -i :8080  # 前端
lsof -i :9000  # 中间层
lsof -i :8000  # 后端

# 停止占用端口的进程
./stop-all.sh
```

---

## 💡 提示

- ✅ 首次启动会自动安装依赖，需要等待几分钟
- ✅ 所有日志文件保存在各服务目录的 `*_service.log`
- ✅ 服务会在后台运行，关闭终端不影响服务
- ✅ 使用 `./status.sh` 随时查看服务状态

---

## 📞 需要帮助？

查看详细文档: [README.md](./README.md)

