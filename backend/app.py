#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web
import json
import logging
from api_handlers import ApiHandlers
from db_session import first_init_db

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建API处理器实例
api_handlers = ApiHandlers()

@web.middleware
async def log_middleware(request, handler):
    """日志中间件"""
    try:
        logger.info(f"请求: {request.method} {request.path}")
        response = await handler(request)
        logger.info(f"响应: {response.status}")
        return response
    except Exception as e:
        logger.error(f"请求处理失败: {e}")
        return web.json_response(
            {"error": str(e), "code": 500}, 
            status=500
        )

@web.middleware
async def cors_middleware(request, handler):
    """CORS中间件"""
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


async def init_app_on_startup(app):
    """应用启动时的初始化函数"""
    try:
        first_init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")

# 创建应用
app = web.Application(client_max_size=2000 * 1024 * 1024)

# 注册中间件
app.middlewares.append(log_middleware)
app.middlewares.append(cors_middleware)

# 注册路由 (改为POST请求，使用下划线路径)
app.router.add_post("/api/template_query_stats", api_handlers.template_query_stats_handler)
app.router.add_post("/api/non_template_query_stats", api_handlers.non_template_query_stats_handler)
app.router.add_post("/api/template_query_errors", api_handlers.template_query_errors_handler)
app.router.add_post("/api/non_template_query_errors", api_handlers.non_template_query_errors_handler)
app.router.add_post("/api/template_query_performance", api_handlers.template_query_performance_handler)
app.router.add_post("/api/non_template_query_performance", api_handlers.non_template_query_performance_handler)
app.router.add_post("/api/step_performance", api_handlers.step_performance_handler)
app.router.add_post("/api/channel_stats", api_handlers.channel_stats_handler)
app.router.add_post("/api/no_ticket_stats", api_handlers.no_ticket_stats_handler)
app.router.add_post("/api/scenario_stats", api_handlers.scenario_stats_handler)
app.router.add_post("/api/user_stats", api_handlers.user_stats_handler)
app.router.add_post("/api/performance_detail", api_handlers.performance_detail_handler)
app.router.add_post("/api/query_trend", api_handlers.query_trend_handler)
app.router.add_post("/api/step_trend", api_handlers.step_trend_handler)
app.router.add_post("/api/channel_trend", api_handlers.channel_trend_handler)

def run():
    """运行应用"""
    # 注册启动钩子
    app.on_startup.append(init_app_on_startup)
    
    # 启动应用
    web.run_app(app, port=8000, host='0.0.0.0')

if __name__ == "__main__":
    run()
