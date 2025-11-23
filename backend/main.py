#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import uvicorn
from database import DatabaseManager
from models import (
    QueryStatsResponse, ErrorStatsResponse, PerformanceStatsResponse, 
    StepPerformanceResponse, ChannelStatsResponse, NoTicketStatsResponse, 
    ScenarioStatsResponse, UserStatsResponse, PerformanceDetailResponse,
    WeeklyQueryTrendResponse, WeeklyStepTrendResponse, WeeklyChannelTrendResponse
)

app = FastAPI(title="大乔工具运营数据管理台", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库管理器
db_manager = DatabaseManager()

@app.get("/")
async def root():
    return {"message": "大乔工具运营数据管理台 API"}

@app.get("/api/template-query/stats", response_model=QueryStatsResponse)
async def get_template_query_stats(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取模板查询统计数据"""
    try:
        stats = db_manager.get_template_query_stats(queryDate)
        return QueryStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/template-query/stats", response_model=QueryStatsResponse)
async def post_template_query_stats(request: Request):
    """获取模板查询统计数据 (POST)"""
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        stats = db_manager.get_template_query_stats(queryDate)
        return QueryStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/non-template-query/stats", response_model=QueryStatsResponse)
async def get_non_template_query_stats(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取非模板查询统计数据"""
    try:
        stats = db_manager.get_non_template_query_stats(queryDate)
        return QueryStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/template-query/errors", response_model=List[ErrorStatsResponse])
async def get_template_query_errors(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取模板查询错误统计"""
    try:
        errors = db_manager.get_template_query_errors(queryDate)
        return [ErrorStatsResponse(**error) for error in errors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/non-template-query/errors", response_model=List[ErrorStatsResponse])
async def get_non_template_query_errors(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取非模板查询错误统计"""
    try:
        errors = db_manager.get_non_template_query_errors(queryDate)
        return [ErrorStatsResponse(**error) for error in errors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/template-query/performance", response_model=List[PerformanceStatsResponse])
async def get_template_query_performance(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取模板查询性能统计"""
    try:
        performance = db_manager.get_template_query_performance(queryDate)
        return [PerformanceStatsResponse(**perf) for perf in performance]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/non-template-query/performance", response_model=List[PerformanceStatsResponse])
async def get_non_template_query_performance(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取非模板查询性能统计"""
    try:
        performance = db_manager.get_non_template_query_performance(queryDate)
        return [PerformanceStatsResponse(**perf) for perf in performance]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/step-performance", response_model=List[StepPerformanceResponse])
async def get_step_performance(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取各个环节的耗时统计"""
    try:
        steps = db_manager.get_step_performance(queryDate)
        return [StepPerformanceResponse(**step) for step in steps]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channel-stats", response_model=List[ChannelStatsResponse])
async def get_channel_stats(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取各个渠道的查询数量统计"""
    try:
        channels = db_manager.get_channel_stats(queryDate)
        return [ChannelStatsResponse(**channel) for channel in channels]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/channel-stats", response_model=List[ChannelStatsResponse])
async def post_channel_stats(request: Request):
    """获取各个渠道的查询数量统计 (POST)"""
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        channels = db_manager.get_channel_stats(queryDate)
        return [ChannelStatsResponse(**channel) for channel in channels]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/no-ticket-stats", response_model=NoTicketStatsResponse)
async def get_no_ticket_stats(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取免提单数量统计"""
    try:
        stats = db_manager.get_no_ticket_stats(queryDate)
        return NoTicketStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenario-stats", response_model=List[ScenarioStatsResponse])
async def get_scenario_stats(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取各个场景的查询数量统计"""
    try:
        scenarios = db_manager.get_scenario_stats(queryDate)
        return [ScenarioStatsResponse(**scenario) for scenario in scenarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-stats", response_model=List[UserStatsResponse])
async def get_user_stats(queryDate: str = Query(..., description="查询日期，格式：YYYY-MM-DD")):
    """获取使用人员统计"""
    try:
        users = db_manager.get_user_stats(queryDate)
        return [UserStatsResponse(**user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance-detail", response_model=PerformanceDetailResponse)
async def get_performance_detail(biz_seq: str = Query(..., description="业务流水号")):
    """获取性能详细分析"""
    try:
        detail = db_manager.get_performance_detail(biz_seq)
        return PerformanceDetailResponse(**detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weekly-query-trend", response_model=List[WeeklyQueryTrendResponse])
async def get_weekly_query_trend(
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD")
):
    """获取查询趋势（支持自定义日期范围）"""
    try:
        trend = db_manager.get_date_range_query_trend(start_date, end_date)
        return [WeeklyQueryTrendResponse(**item) for item in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weekly-step-trend", response_model=List[WeeklyStepTrendResponse])
async def get_weekly_step_trend(
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD")
):
    """获取各环节的耗时趋势（支持自定义日期范围）"""
    try:
        trend = db_manager.get_date_range_step_trend(start_date, end_date)
        return [WeeklyStepTrendResponse(**item) for item in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weekly-channel-trend", response_model=List[WeeklyChannelTrendResponse])
async def get_weekly_channel_trend(
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD")
):
    """获取各渠道的查询趋势（支持自定义日期范围）"""
    try:
        trend = db_manager.get_date_range_channel_trend(start_date, end_date)
        return [WeeklyChannelTrendResponse(**item) for item in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# ============ POST版本的API端点 ============

@app.post("/api/non-template-query/stats", response_model=QueryStatsResponse)
async def post_non_template_query_stats(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        stats = db_manager.get_non_template_query_stats(queryDate)
        return QueryStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/template-query/errors", response_model=List[ErrorStatsResponse])
async def post_template_query_errors(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        errors = db_manager.get_template_query_errors(queryDate)
        return [ErrorStatsResponse(**error) for error in errors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/non-template-query/errors", response_model=List[ErrorStatsResponse])
async def post_non_template_query_errors(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        errors = db_manager.get_non_template_query_errors(queryDate)
        return [ErrorStatsResponse(**error) for error in errors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/template-query/performance", response_model=List[PerformanceStatsResponse])
async def post_template_query_performance(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        performance = db_manager.get_template_query_performance(queryDate)
        return [PerformanceStatsResponse(**perf) for perf in performance]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/non-template-query/performance", response_model=List[PerformanceStatsResponse])
async def post_non_template_query_performance(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        performance = db_manager.get_non_template_query_performance(queryDate)
        return [PerformanceStatsResponse(**perf) for perf in performance]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/step-performance", response_model=List[StepPerformanceResponse])
async def post_step_performance(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        steps = db_manager.get_step_performance(queryDate)
        return [StepPerformanceResponse(**step) for step in steps]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/no-ticket-stats", response_model=NoTicketStatsResponse)
async def post_no_ticket_stats(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        stats = db_manager.get_no_ticket_stats(queryDate)
        return NoTicketStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenario-stats", response_model=List[ScenarioStatsResponse])
async def post_scenario_stats(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        scenarios = db_manager.get_scenario_stats(queryDate)
        return [ScenarioStatsResponse(**scenario) for scenario in scenarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user-stats", response_model=List[UserStatsResponse])
async def post_user_stats(request: Request):
    try:
        body = await request.json()
        queryDate = body.get("queryDate")
        if not queryDate:
            raise HTTPException(status_code=400, detail="queryDate is required")
        users = db_manager.get_user_stats(queryDate)
        return [UserStatsResponse(**user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/performance-detail", response_model=PerformanceDetailResponse)
async def post_performance_detail(request: Request):
    try:
        body = await request.json()
        biz_seq = body.get("bizSeq")
        if not biz_seq:
            raise HTTPException(status_code=400, detail="bizSeq is required")
        detail = db_manager.get_performance_detail(biz_seq)
        return PerformanceDetailResponse(**detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weekly-query-trend", response_model=List[WeeklyQueryTrendResponse])
async def post_weekly_query_trend(request: Request):
    try:
        body = await request.json()
        end_date = body.get("endDate")
        start_date = body.get("startDate")
        trend = db_manager.get_date_range_query_trend(start_date, end_date)
        return [WeeklyQueryTrendResponse(**item) for item in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weekly-step-trend", response_model=List[WeeklyStepTrendResponse])
async def post_weekly_step_trend(request: Request):
    try:
        body = await request.json()
        end_date = body.get("endDate")
        start_date = body.get("startDate")
        trend = db_manager.get_date_range_step_trend(start_date, end_date)
        return [WeeklyStepTrendResponse(**item) for item in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weekly-channel-trend", response_model=List[WeeklyChannelTrendResponse])
async def post_weekly_channel_trend(request: Request):
    try:
        body = await request.json()
        end_date = body.get("endDate")
        start_date = body.get("startDate")
        trend = db_manager.get_date_range_channel_trend(start_date, end_date)
        return [WeeklyChannelTrendResponse(**item) for item in trend]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
