#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryStatsResponse(BaseModel):
    """查询统计响应模型"""
    total_count: int
    success_count: int
    failure_count: int
    success_rate: float
    queryDate: str

class ErrorStatsResponse(BaseModel):
    """错误统计响应模型"""
    subsystem: str  # agent 或 ds
    subsystem_name: str  # 子系统中文名称
    error_code: str
    error_message: str
    count: int
    percentage: float
    total_errors: int

class PerformanceStatsResponse(BaseModel):
    """性能统计响应模型"""
    category: str  # 如 "TDSQL-准生产环境"
    db_type: str  # TDSQL, TIDB, HIVE
    environment: str  # 准生产环境, 生产环境
    avg_cost: float  # 平均耗时（毫秒）
    max_cost: float  # 最大耗时（毫秒）
    max_cost_biz_seq: Optional[str]  # 最大耗时对应的业务流水号

class StepPerformanceResponse(BaseModel):
    """步骤性能响应模型"""
    step_name: str
    step_name_cn: str  # 中文名称
    avg_cost: float  # 平均耗时（毫秒）
    max_cost: float  # 最大耗时（毫秒）

class ChannelStatsResponse(BaseModel):
    """渠道统计响应模型"""
    channel: str
    channel_name: str  # 渠道中文名称
    count: int

class NoTicketStatsResponse(BaseModel):
    """免提单统计响应模型"""
    count: int
    queryDate: str

class ScenarioStatsResponse(BaseModel):
    """场景统计响应模型"""
    scenario: str
    scenario_name: str  # 场景中文名称
    count: int

class UserStatsResponse(BaseModel):
    """用户统计响应模型"""
    user_id: str
    count: int
    rank: int  # 排名

class StepDetailResponse(BaseModel):
    """步骤详细信息响应模型"""
    step_name: str
    sub_step_name: str
    cost: int  # 耗时（毫秒）
    step_name_cn: str  # 中文名称

class PerformanceDetailResponse(BaseModel):
    """性能详细分析响应模型"""
    biz_seq: str
    total_cost: int
    steps: List[StepDetailResponse]
    req_ds_steps: List[StepDetailResponse]  # REQ_DS步骤
    sql_execution_times: List[str]  # SQL实际执行耗时

class WeeklyQueryTrendResponse(BaseModel):
    """一周查询趋势响应模型"""
    date: str
    total_count: int
    template_count: int
    non_template_count: int

class WeeklyStepTrendResponse(BaseModel):
    """一周步骤耗时趋势响应模型"""
    date: str
    step_name: str
    step_name_cn: str
    avg_cost: float

class WeeklyChannelTrendResponse(BaseModel):
    """一周渠道趋势响应模型"""
    date: str
    channel: str
    channel_name: str
    count: int

