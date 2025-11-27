#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from database import DatabaseManager

logger = logging.getLogger(__name__)

class DataService:
    """数据服务类，处理所有数据相关的业务逻辑"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_template_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取模板查询统计数据"""
        try:
            return self.db_manager.get_template_query_stats(queryDate)
        except Exception as e:
            logger.error(f"获取模板查询统计数据失败: {e}")
            raise e
    
    def get_non_template_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取非模板查询统计数据"""
        try:
            return self.db_manager.get_non_template_query_stats(queryDate)
        except Exception as e:
            logger.error(f"获取非模板查询统计数据失败: {e}")
            raise e
    
    def get_template_query_performance(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取模板查询性能统计"""
        try:
            return self.db_manager.get_template_query_performance(queryDate)
        except Exception as e:
            logger.error(f"获取模板查询性能统计失败: {e}")
            raise e
    
    def get_non_template_query_performance(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取非模板查询性能统计"""
        try:
            return self.db_manager.get_non_template_query_performance(queryDate)
        except Exception as e:
            logger.error(f"获取非模板查询性能统计失败: {e}")
            raise e
    
    def get_step_performance(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取各个环节的耗时统计"""
        try:
            return self.db_manager.get_step_performance(queryDate)
        except Exception as e:
            logger.error(f"获取步骤性能统计失败: {e}")
            raise e
    
    def get_channel_stats(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取各个渠道的查询数量统计"""
        try:
            return self.db_manager.get_channel_stats(queryDate)
        except Exception as e:
            logger.error(f"获取渠道统计失败: {e}")
            raise e
    
    def get_no_ticket_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取免提单数量统计"""
        try:
            return self.db_manager.get_no_ticket_stats(queryDate)
        except Exception as e:
            logger.error(f"获取免提单统计失败: {e}")
            raise e
    
    def get_scenario_stats(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取各个场景的查询数量统计"""
        try:
            return self.db_manager.get_scenario_stats(queryDate)
        except Exception as e:
            logger.error(f"获取场景统计失败: {e}")
            raise e
    
    def get_user_stats(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取使用人员统计"""
        try:
            return self.db_manager.get_user_stats(queryDate)
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            raise e
    
    def get_performance_detail(self, biz_seq: str) -> Dict[str, Any]:
        """获取性能详细分析"""
        try:
            return self.db_manager.get_performance_detail(biz_seq)
        except Exception as e:
            logger.error(f"获取性能详细分析失败: {e}")
            raise e
    
    def get_date_range_query_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的查询趋势"""
        try:
            return self.db_manager.get_date_range_query_trend(start_date, end_date)
        except Exception as e:
            logger.error(f"获取日期范围查询趋势失败: {e}")
            raise e
    
    def get_date_range_step_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的各环节耗时趋势"""
        try:
            return self.db_manager.get_date_range_step_trend(start_date, end_date)
        except Exception as e:
            logger.error(f"获取日期范围步骤趋势失败: {e}")
            raise e
    
    def get_date_range_channel_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的各渠道查询趋势"""
        try:
            return self.db_manager.get_date_range_channel_trend(start_date, end_date)
        except Exception as e:
            logger.error(f"获取日期范围渠道趋势失败: {e}")
            raise e
    
    def get_agent_error_details(self, queryDate: str) -> Dict[str, Any]:
        """获取Agent子系统错误明细数据"""
        try:
            return self.db_manager.get_agent_error_details(queryDate)
        except Exception as e:
            logger.error(f"获取Agent错误明细失败: {e}")
            raise e
    
    def get_ds_error_details(self, queryDate: str) -> Dict[str, Any]:
        """获取DS子系统错误明细数据"""
        try:
            return self.db_manager.get_ds_error_details(queryDate)
        except Exception as e:
            logger.error(f"获取DS错误明细失败: {e}")
            raise e
