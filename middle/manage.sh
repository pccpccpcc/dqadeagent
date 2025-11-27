#!/bin/bash
# Middle服务管理脚本

MIDDLE_DIR="/Users/pengchengchen/Desktop/dqadeagent/middle"
PID_FILE="$MIDDLE_DIR/service.pid"
LOG_FILE="$MIDDLE_DIR/middle_service.log"
JAR_FILE="$MIDDLE_DIR/target/middle-1.0.0.jar"

cd "$MIDDLE_DIR"

# 获取当前运行的服务PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        ps aux | grep "middle-1.0.0.jar" | grep -v grep | awk '{print $2}' | head -1
    fi
}

# 检查服务状态
status() {
    PID=$(get_pid)
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Middle服务正在运行 (PID: $PID)"
        echo "   端口: 9000"
        echo "   地址: http://localhost:9000"
        echo "   健康检查: http://localhost:9000/api/health"
        return 0
    else
        echo "❌ Middle服务未运行"
        return 1
    fi
}

# 启动服务
start() {
    if status > /dev/null 2>&1; then
        echo "⚠️  服务已在运行"
        status
        return 1
    fi
    
    echo "正在启动Middle服务..."
    
    # 检查JAR文件
    if [ ! -f "$JAR_FILE" ]; then
        echo "❌ JAR文件不存在: $JAR_FILE"
        echo "   请先运行: mvn clean package"
        return 1
    fi
    
    # 检查Java环境
    if ! command -v java &> /dev/null; then
        echo "❌ 未找到Java"
        return 1
    fi
    
    echo "✓ Java版本: $(java -version 2>&1 | head -1)"
    
    # 启动服务
    nohup java -jar "$JAR_FILE" > "$LOG_FILE" 2>&1 &
    
    sleep 5
    
    # 获取实际的Java进程PID
    PID=$(ps aux | grep "middle-1.0.0.jar" | grep -v grep | awk '{print $2}' | head -1)
    
    if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
        echo $PID > "$PID_FILE"
        echo "✅ Middle服务启动成功 (PID: $PID)"
        echo "   地址: http://localhost:9000"
        echo "   健康检查: http://localhost:9000/api/health"
        echo "   日志: $LOG_FILE"
    else
        echo "❌ 服务启动失败，查看日志: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 停止服务
stop() {
    PID=$(get_pid)
    if [ -z "$PID" ]; then
        echo "⚠️  服务未运行"
        rm -f "$PID_FILE"
        return 0
    fi
    
    echo "正在停止Middle服务 (PID: $PID)..."
    kill $PID 2>/dev/null
    
    # 等待最多15秒
    for i in {1..15}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "✅ 服务已停止"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done
    
    # 强制停止
    echo "⚠️  正在强制停止服务..."
    kill -9 $PID 2>/dev/null
    rm -f "$PID_FILE"
    echo "✅ 服务已强制停止"
}

# 重启服务
restart() {
    echo "正在重启Middle服务..."
    stop
    sleep 2
    start
}

# 查看日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "❌ 日志文件不存在: $LOG_FILE"
        return 1
    fi
}

# 测试服务
test() {
    if ! status > /dev/null 2>&1; then
        echo "❌ 服务未运行"
        return 1
    fi
    
    echo "正在测试Middle服务..."
    
    # 测试健康检查
    echo -n "测试健康检查接口... "
    RESPONSE=$(curl -s http://localhost:9000/api/health)
    if echo "$RESPONSE" | grep -q "ok"; then
        echo "✅"
    else
        echo "❌"
    fi
    
    # 测试代理接口
    echo -n "测试代理接口... "
    RESPONSE=$(curl -s -X POST http://localhost:9000/api/proxy \
      -H "Content-Type: application/json" \
      -d '{"path":"/api/template-query/stats","queryDate":"2024-11-20"}')
    if echo "$RESPONSE" | grep -q "code"; then
        echo "✅"
    else
        echo "❌"
    fi
    
    echo ""
    echo "✅ Middle服务测试完成"
}

# 编译项目
build() {
    echo "正在编译Middle项目..."
    
    if ! command -v mvn &> /dev/null; then
        echo "❌ 未找到Maven"
        return 1
    fi
    
    mvn clean package -DskipTests
    
    if [ $? -eq 0 ]; then
        echo "✅ 编译成功"
    else
        echo "❌ 编译失败"
        return 1
    fi
}

# 主函数
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    test)
        test
        ;;
    build)
        build
        ;;
    *)
        echo "Middle服务管理脚本"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs|test|build}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看实时日志"
        echo "  test    - 测试服务接口"
        echo "  build   - 编译项目"
        echo ""
        exit 1
        ;;
esac






