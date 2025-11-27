#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
import json
from decimal import Decimal
from data_service import DataService

logger = logging.getLogger(__name__)

def convert_decimals(obj):
    """递归转换所有Decimal类型为float"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj

class DecimalEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理Decimal类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class ApiHandlers:
    """API处理器类，包含所有HTTP请求的处理逻辑"""
    
    def __init__(self):
        self.data_service = DataService()
    
    async def template_query_stats_handler(self, request: web.Request):
        """获取模板查询统计数据"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            stats = self.data_service.get_template_query_stats(queryDate)
            # 转换Decimal类型
            stats = convert_decimals(stats)
            return web.json_response({"data": stats, "code": 200})
        except Exception as e:
            logger.error(f"获取模板查询统计数据失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def non_template_query_stats_handler(self, request: web.Request):
        """获取非模板查询统计数据"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            stats = self.data_service.get_non_template_query_stats(queryDate)
            # 转换Decimal类型
            stats = convert_decimals(stats)
            return web.json_response({"data": stats, "code": 200})
        except Exception as e:
            logger.error(f"获取非模板查询统计数据失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def template_query_performance_handler(self, request: web.Request):
        """获取模板查询性能统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            performance = self.data_service.get_template_query_performance(queryDate)
            # 转换Decimal类型
            performance = convert_decimals(performance)
            return web.json_response({"data": performance, "code": 200})
        except Exception as e:
            logger.error(f"获取模板查询性能统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def non_template_query_performance_handler(self, request: web.Request):
        """获取非模板查询性能统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            performance = self.data_service.get_non_template_query_performance(queryDate)
            # 转换Decimal类型
            performance = convert_decimals(performance)
            return web.json_response({"data": performance, "code": 200})
        except Exception as e:
            logger.error(f"获取非模板查询性能统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def step_performance_handler(self, request: web.Request):
        """获取各个环节的耗时统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            steps = self.data_service.get_step_performance(queryDate)
            # 确保转换所有Decimal类型
            steps = convert_decimals(steps)
            return web.json_response({"data": steps, "code": 200})
        except Exception as e:
            logger.error(f"获取步骤性能统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def channel_stats_handler(self, request: web.Request):
        """获取各个渠道的查询数量统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            channels = self.data_service.get_channel_stats(queryDate)
            return web.json_response({"data": channels, "code": 200})
        except Exception as e:
            logger.error(f"获取渠道统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def no_ticket_stats_handler(self, request: web.Request):
        """获取免提单数量统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            stats = self.data_service.get_no_ticket_stats(queryDate)
            return web.json_response({"data": stats, "code": 200})
        except Exception as e:
            logger.error(f"获取免提单统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def scenario_stats_handler(self, request: web.Request):
        """获取各个场景的查询数量统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            scenarios = self.data_service.get_scenario_stats(queryDate)
            return web.json_response({"data": scenarios, "code": 200})
        except Exception as e:
            logger.error(f"获取场景统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def user_stats_handler(self, request: web.Request):
        """获取使用人员统计"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            users = self.data_service.get_user_stats(queryDate)
            return web.json_response({"data": users, "code": 200})
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def performance_detail_handler(self, request: web.Request):
        """获取性能详细分析"""
        try:
            data = await request.json()
            bizSeq = data.get('bizSeq')
            if not bizSeq:
                return web.json_response(
                    {"error": "缺少bizSeq参数", "code": 400},
                    status=400
                )

            detail = self.data_service.get_performance_detail(bizSeq)
            return web.json_response({"data": detail, "code": 200})
        except Exception as e:
            logger.error(f"获取性能详细分析失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def query_trend_handler(self, request: web.Request):
        """获取查询趋势"""
        try:
            data = await request.json()
            startDate = data.get('startDate')
            endDate = data.get('endDate')

            trend = self.data_service.get_date_range_query_trend(startDate, endDate)
            return web.json_response({"data": trend, "code": 200})
        except Exception as e:
            logger.error(f"获取查询趋势失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def step_trend_handler(self, request: web.Request):
        """获取各环节的耗时趋势"""
        try:
            data = await request.json()
            startDate = data.get('startDate')
            endDate = data.get('endDate')

            trend = self.data_service.get_date_range_step_trend(startDate, endDate)
            return web.json_response({"data": trend, "code": 200})
        except Exception as e:
            logger.error(f"获取步骤趋势失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )

    async def channel_trend_handler(self, request: web.Request):
        """获取各渠道的查询趋势"""
        try:
            data = await request.json()
            startDate = data.get('startDate')
            endDate = data.get('endDate')

            trend = self.data_service.get_date_range_channel_trend(startDate, endDate)
            return web.json_response({"data": trend, "code": 200})
        except Exception as e:
            logger.error(f"获取渠道趋势失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )
    
    async def agent_error_details_handler(self, request: web.Request):
        """获取Agent子系统错误明细数据"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            details = self.data_service.get_agent_error_details(queryDate)
            return web.json_response({"data": details, "code": 200})
        except Exception as e:
            logger.error(f"获取Agent错误明细失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )
    
    async def ds_error_details_handler(self, request: web.Request):
        """获取DS子系统错误明细数据"""
        try:
            data = await request.json()
            queryDate = data.get('queryDate')
            if not queryDate:
                return web.json_response(
                    {"error": "缺少queryDate参数", "code": 400},
                    status=400
                )

            details = self.data_service.get_ds_error_details(queryDate)
            return web.json_response({"data": details, "code": 200})
        except Exception as e:
            logger.error(f"获取DS错误明细失败: {e}")
            return web.json_response(
                {"error": str(e), "code": 500}, 
                status=500
            )