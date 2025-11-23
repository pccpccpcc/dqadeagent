#!/bin/bash
# Backend服务管理脚本

BACKEND_DIR="/Users/pengchengchen/Desktop/dqadeagent/backend"
PID_FILE="$BACKEND_DIR/service.pid"
LOG_FILE="$BACKEND_DIR/uvicorn.log"

cd "$BACKEND_DIR"

# 获取当前运行的服务PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        lsof -ti :8000 2>/dev/null | head -1
    fi
}

# 检查服务状态
status() {
    PID=$(get_pid)
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ 服务正在运行 (PID: $PID)"
        echo "   端口: 8000"
        echo "   地址: http://localhost:8000"
        echo "   文档: http://localhost:8000/docs"
        return 0
    else
        echo "❌ 服务未运行"
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
    
    echo "正在启动Backend服务..."
    
    # 测试数据库连接
    python3 -c "from db_session import get_db_session; s=get_db_session(); s.close()" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ 数据库连接失败"
        return 1
    fi
    echo "✓ 数据库连接正常"
    
    # 启动服务
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    sleep 3
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务启动成功 (PID: $PID)"
        echo "   地址: http://localhost:8000"
        echo "   文档: http://localhost:8000/docs"
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
    
    echo "正在停止服务 (PID: $PID)..."
    kill $PID 2>/dev/null
    
    # 等待最多10秒
    for i in {1..10}; do
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
    echo "正在重启服务..."
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
    
    echo "正在测试API接口..."
    
    # 测试根路径
    echo -n "测试根路径... "
    RESPONSE=$(curl -s http://localhost:8000/)
    if echo "$RESPONSE" | grep -q "大乔工具"; then
        echo "✅"
    else
        echo "❌"
    fi
    
    # 测试业务接口
    echo -n "测试业务接口... "
    RESPONSE=$(curl -s "http://localhost:8000/api/template-query/stats?queryDate=2024-11-20")
    if echo "$RESPONSE" | grep -q "queryDate"; then
        echo "✅"
    else
        echo "❌"
    fi
    
    echo ""
    echo "✅ 服务测试完成"
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
    *)
        echo "Backend服务管理脚本"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看实时日志"
        echo "  test    - 测试服务接口"
        echo ""
        exit 1
        ;;
esac

