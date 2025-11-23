#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import text
from db_session import get_db_session

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # 使用SQLAlchemy session，不再需要连接参数
        
        # 错误码映射
        self.agent_error_codes = {
            '1': '客户端请求错误（请求本身有问题，需客户端修正）',
            '2': '权限与认证错误',
            '3': '服务调用错误',
            '4': '数据访问错误',
            '9': '服务端内部发生了未预期的内部异常'
        }
        
        self.ds_error_codes = {
            '0001': '参数错误',
            '0098': '子系统数据库/表名/dcn等信息异常',
            '0099': 'sql error',
            '0101': 'SQL执行结果查询超时',
            '0102': '请求aomp异常',
            '0103': 'other error',
            '0104': '验签失败',
            '1001': '查询元数据信息异常！',
            '2001': '提交SQL发送异常！',
            '2002': 'SQL执行超时！',
            '3001': 'AOMP返回结果为空！'
        }
        
        self.step_name_mapping = {
            'INFO_EXTRACTION_LLM': '信息提取',
            'SQL_EXTRACTION_LLM': '字段提取',
            'QUERY_SCHEMA': '表结构查询',
            'QUERY_INTENT': '查询意图识别',
            'SUB_QUERY': '子模块查询',
            'RESULT_DEAL': '查询结果处理'
        }
        
        self.channel_name_mapping = {
            'DKK': 'DKK渠道',
            'DQ_WEB': 'DQ_WEB渠道',
            'DQ_QW': 'DQ_QW渠道',
            'WXB-_QW': 'WXB-_QW渠道',
            'XQ_DIFY': 'XQ_DIFY渠道'
        }

    def execute_query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行查询"""
        session = get_db_session()
        try:
            # 使用SQLAlchemy的text()函数执行原生SQL
            # 在SQLAlchemy 2.0.40中，需要将位置参数转换为字典形式
            if params:
                # 将位置参数转换为字典形式，使用参数索引作为键
                param_dict = {f'param_{i}': param for i, param in enumerate(params)}
                # 将SQL中的%s替换为命名参数
                modified_sql = sql
                for i in range(len(params)):
                    modified_sql = modified_sql.replace('%s', f':param_{i}', 1)
                result = session.execute(text(modified_sql), param_dict)
            else:
                result = session.execute(text(sql))
            # 将结果转换为字典列表
            columns = result.keys()
            rows = result.fetchall()
            # 处理Decimal类型的数据转换为float
            from decimal import Decimal
            formatted_rows = []
            for row in rows:
                formatted_row = {}
                for col, val in zip(columns, row):
                    if isinstance(val, Decimal):
                        formatted_row[col] = float(val)
                    else:
                        formatted_row[col] = val
                formatted_rows.append(formatted_row)
            return formatted_rows
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise e
        finally:
            session.close()

    def get_template_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取模板查询统计数据"""
        try:
            # 转换日期格式
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj + timedelta(days=1)
            
            # 总数
            total_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s AND req_info LIKE %s
            """
            total_result = self.execute_query(total_sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%###%'))
            total_count = total_result[0]['count'] if total_result else 0
            
            # 成功数
            success_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s AND req_info LIKE %s AND result_code LIKE %s
            """
            success_result = self.execute_query(success_sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%###%', '%0000%'))
            success_count = success_result[0]['count'] if success_result else 0
            
            # 失败数
            failure_count = total_count - success_count
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            return {
                'total_count': total_count,
                'success_count': success_count,
                'failure_count': failure_count,
                'success_rate': round(success_rate, 2),
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取模板查询统计数据失败: {e}")
            raise e

    def get_non_template_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取非模板查询统计数据"""
        try:
            # 转换日期格式
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj + timedelta(days=1)
            
            # 总数
            total_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s AND req_info NOT LIKE %s
            """
            total_result = self.execute_query(total_sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%###%'))
            total_count = total_result[0]['count'] if total_result else 0
            
            # 成功数
            success_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s AND req_info NOT LIKE %s AND result_code LIKE %s
            """
            success_result = self.execute_query(success_sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%###%', '%0000%'))
            success_count = success_result[0]['count'] if success_result else 0
            
            # 失败数
            failure_count = total_count - success_count
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            return {
                'total_count': total_count,
                'success_count': success_count,
                'failure_count': failure_count,
                'success_rate': round(success_rate, 2),
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取非模板查询统计数据失败: {e}")
            raise e

    def _parse_error_code(self, result_code: str) -> Dict[str, str]:
        """解析错误码"""
        subsystem_code = result_code[:4]
        
        if subsystem_code == 'B2DU':
            # agent子系统
            error_code = result_code[6] if len(result_code) > 6 else '0'
            error_message = self.agent_error_codes.get(error_code, '未知错误')
            return {
                'subsystem': 'agent',
                'subsystem_name': 'Agent子系统',
                'error_code': error_code,
                'error_message': error_message
            }
        elif subsystem_code == '2030':
            # ds子系统
            error_code = result_code[-4:] if len(result_code) >= 4 else '0000'
            error_message = self.ds_error_codes.get(error_code, '未知错误')
            return {
                'subsystem': 'ds',
                'subsystem_name': 'DS子系统',
                'error_code': error_code,
                'error_message': error_message
            }
        else:
            return {
                'subsystem': 'unknown',
                'subsystem_name': '未知子系统',
                'error_code': result_code,
                'error_message': '未知错误'
            }

    def get_template_query_errors(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取模板查询错误统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            sql = """
                SELECT result_code FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND req_info LIKE %s AND result_code NOT LIKE %s
            """
            results = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%###%', '%0000%'))
            
            # 统计错误码
            error_stats = {}
            total_errors = len(results)
            
            for row in results:
                error_info = self._parse_error_code(row['result_code'])
                key = f"{error_info['subsystem']}_{error_info['error_code']}"
                
                if key not in error_stats:
                    error_stats[key] = {
                        'subsystem': error_info['subsystem'],
                        'subsystem_name': error_info['subsystem_name'],
                        'error_code': error_info['error_code'],
                        'error_message': error_info['error_message'],
                        'count': 0
                    }
                error_stats[key]['count'] += 1
            
            # 计算百分比
            result = []
            for error in error_stats.values():
                error['percentage'] = round(error['count'] / total_errors * 100, 2) if total_errors > 0 else 0
                error['total_errors'] = total_errors
                result.append(error)
            
            return sorted(result, key=lambda x: x['count'], reverse=True)
        except Exception as e:
            logger.error(f"获取模板查询错误统计失败: {e}")
            raise e

    def get_non_template_query_errors(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取非模板查询错误统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            sql = """
                SELECT result_code FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND req_info NOT LIKE %s AND result_code NOT LIKE %s
            """
            results = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%###%', '%0000%'))
            
            # 统计错误码
            error_stats = {}
            total_errors = len(results)
            
            for row in results:
                error_info = self._parse_error_code(row['result_code'])
                key = f"{error_info['subsystem']}_{error_info['error_code']}"
                
                if key not in error_stats:
                    error_stats[key] = {
                        'subsystem': error_info['subsystem'],
                        'subsystem_name': error_info['subsystem_name'],
                        'error_code': error_info['error_code'],
                        'error_message': error_info['error_message'],
                        'count': 0
                    }
                error_stats[key]['count'] += 1
            
            # 计算百分比
            result = []
            for error in error_stats.values():
                error['percentage'] = round(error['count'] / total_errors * 100, 2) if total_errors > 0 else 0
                error['total_errors'] = total_errors
                result.append(error)
            
            return sorted(result, key=lambda x: x['count'], reverse=True)
        except Exception as e:
            logger.error(f"获取非模板查询错误统计失败: {e}")
            raise e

    def get_template_query_performance(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取模板查询性能统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            performance_queries = [
                {
                    'category': 'TDSQL-准生产环境',
                    'db_type': 'TDSQL',
                    'environment': '准生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info LIKE %s
                            ) 
                            AND biz_seq NOT IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TDSQL%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'TDSQL-生产环境',
                    'db_type': 'TDSQL',
                    'environment': '生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info LIKE %s
                            ) 
                            AND biz_seq IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TDSQL%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'TIDB-准生产环境',
                    'db_type': 'TIDB',
                    'environment': '准生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info LIKE %s
                            ) 
                            AND biz_seq NOT IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TIDB%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'TIDB-生产环境',
                    'db_type': 'TIDB',
                    'environment': '生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info LIKE %s
                            ) 
                            AND biz_seq IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TIDB%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'HIVE-生产环境',
                    'db_type': 'HIVE',
                    'environment': '生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info LIKE %s
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%HIVE%', '%###%')
                }
            ]
            
            results = []
            for query_info in performance_queries:
                result = self.execute_query(query_info['sql'], query_info['params'])
                if result and result[0]['avg_cost'] is not None:
                    # 获取最大耗时对应的biz_seq
                    max_cost = result[0]['max_cost']
                    max_biz_seq_sql = """
                        SELECT biz_seq FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            GROUP BY biz_seq 
                            HAVING cost = %s
                        ) temp LIMIT 1
                    """
                    max_biz_seq_result = self.execute_query(max_biz_seq_sql, (queryDate, next_date.strftime('%Y-%m-%d'), max_cost))
                    max_cost_biz_seq = max_biz_seq_result[0]['biz_seq'] if max_biz_seq_result else None
                    
                    results.append({
                        'category': query_info['category'],
                        'db_type': query_info['db_type'],
                        'environment': query_info['environment'],
                        'avg_cost': round(float(result[0]['avg_cost']), 2),
                        'max_cost': result[0]['max_cost'],
                        'max_cost_biz_seq': max_cost_biz_seq
                    })
            
            return results
        except Exception as e:
            logger.error(f"获取模板查询性能统计失败: {e}")
            raise e

    def get_non_template_query_performance(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取非模板查询性能统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            performance_queries = [
                {
                    'category': 'TDSQL-准生产环境',
                    'db_type': 'TDSQL',
                    'environment': '准生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info NOT LIKE %s
                            ) 
                            AND biz_seq NOT IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TDSQL%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'TDSQL-生产环境',
                    'db_type': 'TDSQL',
                    'environment': '生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info NOT LIKE %s
                            ) 
                            AND biz_seq IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TDSQL%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'TIDB-准生产环境',
                    'db_type': 'TIDB',
                    'environment': '准生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info NOT LIKE %s
                            ) 
                            AND biz_seq NOT IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TIDB%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'TIDB-生产环境',
                    'db_type': 'TIDB',
                    'environment': '生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info NOT LIKE %s
                            ) 
                            AND biz_seq IN (
                                SELECT DISTINCT biz_seq FROM req_aomp_log 
                                WHERE create_time >= %s AND create_time < %s 
                                AND biz_seq IS NOT NULL
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%TIDB%', '%###%', queryDate, next_date.strftime('%Y-%m-%d'))
                },
                {
                    'category': 'HIVE-生产环境',
                    'db_type': 'HIVE',
                    'environment': '生产环境',
                    'sql': """
                        SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            AND biz_seq IN (
                                SELECT biz_seq FROM t_handler_logs 
                                WHERE create_time >= %s AND create_time < %s 
                                AND req_info LIKE %s AND req_info NOT LIKE %s
                            ) 
                            GROUP BY biz_seq
                        ) temp
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), queryDate, next_date.strftime('%Y-%m-%d'), '%HIVE%', '%###%')
                }
            ]
            
            results = []
            for query_info in performance_queries:
                result = self.execute_query(query_info['sql'], query_info['params'])
                if result and result[0]['avg_cost'] is not None:
                    # 获取最大耗时对应的biz_seq
                    max_cost = result[0]['max_cost']
                    max_biz_seq_sql = """
                        SELECT biz_seq FROM (
                            SELECT biz_seq, SUM(cost) as cost FROM t_step_time_record 
                            WHERE create_time >= %s AND create_time < %s 
                            AND sub_step_name != 'REQ_DS' 
                            GROUP BY biz_seq 
                            HAVING cost = %s
                        ) temp LIMIT 1
                    """
                    max_biz_seq_result = self.execute_query(max_biz_seq_sql, (queryDate, next_date.strftime('%Y-%m-%d'), max_cost))
                    max_cost_biz_seq = max_biz_seq_result[0]['biz_seq'] if max_biz_seq_result else None
                    
                    results.append({
                        'category': query_info['category'],
                        'db_type': query_info['db_type'],
                        'environment': query_info['environment'],
                        'avg_cost': round(float(result[0]['avg_cost']), 2),
                        'max_cost': result[0]['max_cost'],
                        'max_cost_biz_seq': max_cost_biz_seq
                    })
            
            return results
        except Exception as e:
            logger.error(f"获取非模板查询性能统计失败: {e}")
            raise e

    def get_step_performance(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取各个环节的耗时统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            results = []
            for step_name, step_name_cn in self.step_name_mapping.items():
                sql = f"""
                    SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost 
                    FROM t_step_time_record 
                    WHERE create_time >= %s AND create_time < %s 
                    AND step_name = %s
                """
                
                # 对特定步骤添加额外条件
                if step_name == 'QUERY_SCHEMA':
                    sql += """ AND biz_seq NOT IN (
                        SELECT biz_seq FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND req_info LIKE %s
                    ) AND cost > 1000"""
                    params = (queryDate, next_date.strftime('%Y-%m-%d'), step_name, queryDate, next_date.strftime('%Y-%m-%d'), '%HIVE%')
                elif step_name == 'SUB_QUERY':
                    sql += """ AND biz_seq NOT IN (
                        SELECT biz_seq FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND req_info LIKE %s
                    )"""
                    params = (queryDate, next_date.strftime('%Y-%m-%d'), step_name, queryDate, next_date.strftime('%Y-%m-%d'), '%HIVE%')
                else:
                    params = (queryDate, next_date.strftime('%Y-%m-%d'), step_name)
                
                result = self.execute_query(sql, params)
                if result and result[0]['avg_cost'] is not None:
                    # 确保处理Decimal类型
                    from decimal import Decimal
                    avg_cost = result[0]['avg_cost']
                    max_cost = result[0]['max_cost']
                    
                    # 转换Decimal为float
                    if isinstance(avg_cost, Decimal):
                        avg_cost = float(avg_cost)
                    if isinstance(max_cost, Decimal):
                        max_cost = float(max_cost)
                    
                    results.append({
                        'step_name': step_name,
                        'step_name_cn': step_name_cn,
                        'avg_cost': round(avg_cost, 2),
                        'max_cost': max_cost
                    })
            
            return results
        except Exception as e:
            logger.error(f"获取步骤性能统计失败: {e}")
            raise e

    def get_channel_stats(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取各个渠道的查询数量统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            sql = """
                SELECT channel, COUNT(1) as count 
                FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                GROUP BY channel
            """
            results = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            
            formatted_results = []
            for result in results:
                channel = result['channel'] or '未知渠道'
                channel_name = self.channel_name_mapping.get(channel, channel)
                formatted_results.append({
                    'channel': channel,
                    'channel_name': channel_name,
                    'count': result['count']
                })
            
            return sorted(formatted_results, key=lambda x: x['count'], reverse=True)
        except Exception as e:
            logger.error(f"获取渠道统计失败: {e}")
            raise e

    def get_no_ticket_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取免提单数量统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND req_info LIKE %s AND rsp_info LIKE %s
            """
            result = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%"sysNameList": []%', '%查询执行成功%'))
            
            return {
                'count': result[0]['count'] if result else 0,
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取免提单统计失败: {e}")
            raise e

    def get_scenario_stats(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取各个场景的查询数量统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            scenario_queries = [
                {
                    'scenario': 'execution_plan',
                    'scenario_name': '执行计划',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%')
                },
                {
                    'scenario': 'yn_query',
                    'scenario_name': 'Y/N查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%')
                },
                {
                    'scenario': 'count_query',
                    'scenario_name': '数量查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%')
                },
                {
                    'scenario': 'table_structure',
                    'scenario_name': '表结构查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (UPPER(req_info) LIKE %s OR UPPER(req_info) LIKE %s) 
                        AND UPPER(req_info) NOT LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%', '%DESC%', '%SHOW%', '%SELECT%')
                },
                {
                    'scenario': 'enum_query',
                    'scenario_name': '枚举查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (UPPER(req_info) NOT LIKE %s OR UPPER(req_info) LIKE %s) 
                        AND UPPER(req_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%', '%SHOW%', '%DESC%', '%SELECT%', '%DISTINCT%')
                },
                {
                    'scenario': 'time_query',
                    'scenario_name': '时间查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (UPPER(req_info) NOT LIKE %s OR UPPER(req_info) LIKE %s) 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%', '%SHOW%', '%DESC%', '%SELECT%', '%DISTINCT%', '%TIME%FROM%')
                },
                {
                    'scenario': 'config_query',
                    'scenario_name': '配置查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(rsp_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%SQL_TITLE%配置%')
                },
                {
                    'scenario': 'field_length',
                    'scenario_name': '字段长度查询',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (UPPER(req_info) NOT LIKE %s OR UPPER(req_info) LIKE %s) 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%', '%SHOW%', '%DESC%', '%SELECT%', '%DISTINCT%', '%TIME%FROM%', '%LENGTH%')
                },
                {
                    'scenario': 'ticket_related',
                    'scenario_name': '提单相关',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (UPPER(req_info) NOT LIKE %s OR UPPER(req_info) LIKE %s) 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (req_info LIKE %s OR req_info LIKE %s OR req_info LIKE %s OR rsp_info LIKE %s OR rsp_info LIKE %s)
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%', '%SHOW%', '%DESC%', '%SELECT%', '%DISTINCT%', '%TIME%FROM%', '%提单%', '%确认%', '%同意%', '%很荣幸能够%', '%用户协议%')
                },
                {
                    'scenario': 'other',
                    'scenario_name': '其他',
                    'sql': """
                        SELECT COUNT(1) as count FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND (UPPER(req_info) NOT LIKE %s OR UPPER(req_info) LIKE %s) 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND UPPER(req_info) NOT LIKE %s 
                        AND req_info NOT LIKE %s 
                        AND req_info NOT LIKE %s 
                        AND req_info NOT LIKE %s 
                        AND rsp_info NOT LIKE %s 
                        AND rsp_info NOT LIKE %s
                    """,
                    'params': (queryDate, next_date.strftime('%Y-%m-%d'), '%EXPLAIN%', '%IF(%', '%COUNT%', '%SHOW%', '%DESC%', '%SELECT%', '%DISTINCT%', '%TIME%FROM%', '%提单%', '%确认%', '%同意%', '%很荣幸能够%', '%用户协议%')
                }
            ]
            
            results = []
            for query_info in scenario_queries:
                result = self.execute_query(query_info['sql'], query_info['params'])
                results.append({
                    'scenario': query_info['scenario'],
                    'scenario_name': query_info['scenario_name'],
                    'count': result[0]['count'] if result else 0
                })
            
            return sorted(results, key=lambda x: x['count'], reverse=True)
        except Exception as e:
            logger.error(f"获取场景统计失败: {e}")
            raise e

    def get_user_stats(self, queryDate: str) -> List[Dict[str, Any]]:
        """获取使用人员统计"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            sql = """
                SELECT user_id, COUNT(1) as count 
                FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                GROUP BY user_id 
                ORDER BY count DESC
            """
            results = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append({
                    'user_id': result['user_id'] or '未知用户',
                    'count': result['count'],
                    'rank': i
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            raise e

    def get_performance_detail(self, biz_seq: str) -> Dict[str, Any]:
        """获取性能详细分析"""
        try:
            # 获取步骤详情
            steps_sql = """
                SELECT step_name, sub_step_name, cost 
                FROM t_step_time_record 
                WHERE biz_seq = %s 
                ORDER BY create_time
            """
            steps_result = self.execute_query(steps_sql, (biz_seq,))
            
            steps = []
            req_ds_steps = []
            total_cost = 0
            
            for step in steps_result:
                if step['sub_step_name'] == 'REQ_DS':
                    req_ds_steps.append({
                        'step_name': step['step_name'],
                        'sub_step_name': step['sub_step_name'],
                        'cost': step['cost'],
                        'step_name_cn': self.step_name_mapping.get(step['step_name'], step['step_name'])
                    })
                else:
                    steps.append({
                        'step_name': step['step_name'],
                        'sub_step_name': step['sub_step_name'],
                        'cost': step['cost'],
                        'step_name_cn': self.step_name_mapping.get(step['step_name'], step['step_name'])
                    })
                    total_cost += step['cost']
            
            # 获取SQL执行耗时
            sql_time_sql = """
                SELECT sql_execute_time FROM query_sql_log 
                WHERE biz_seq = %s
            """
            sql_time_result = self.execute_query(sql_time_sql, (biz_seq,))
            sql_execution_times = [row['sql_execute_time'] for row in sql_time_result if row['sql_execute_time']]
            
            return {
                'biz_seq': biz_seq,
                'total_cost': total_cost,
                'steps': steps,
                'req_ds_steps': req_ds_steps,
                'sql_execution_times': sql_execution_times
            }
        except Exception as e:
            logger.error(f"获取性能详细分析失败: {e}")
            raise e

    def get_date_range_query_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的查询趋势"""
        try:
            # 如果没有指定日期范围，默认查询最近7天
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            if not start_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                start_date_obj = end_date_obj - timedelta(days=6)  # 包含今天共7天
                start_date = start_date_obj.strftime('%Y-%m-%d')
            
            # 计算日期范围
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            results = []
            current_date = start_date_obj
            
            while current_date <= end_date_obj:
                next_date = current_date + timedelta(days=1)
                
                # 总查询数
                total_sql = """
                    SELECT COUNT(1) as count FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s
                """
                total_result = self.execute_query(total_sql, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')))
                total_count = total_result[0]['count'] if total_result else 0
                
                # 模板查询数
                template_sql = """
                    SELECT COUNT(1) as count FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s AND req_info LIKE %s
                """
                template_result = self.execute_query(template_sql, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), '%###%'))
                template_count = template_result[0]['count'] if template_result else 0
                
                # 非模板查询数
                non_template_count = total_count - template_count
                
                results.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'total_count': total_count,
                    'template_count': template_count,
                    'non_template_count': non_template_count
                })
                
                current_date += timedelta(days=1)
            
            return results
        except Exception as e:
            logger.error(f"获取日期范围查询趋势失败: {e}")
            raise e

    def get_weekly_query_trend(self, end_date: str) -> List[Dict[str, Any]]:
        """获取最近一周的查询趋势"""
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            results = []
            
            for i in range(7):
                current_date = end_date_obj - timedelta(days=i)
                next_date = current_date + timedelta(days=1)
                
                # 总查询数
                total_sql = """
                    SELECT COUNT(1) as count FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s
                """
                total_result = self.execute_query(total_sql, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')))
                total_count = total_result[0]['count'] if total_result else 0
                
                # 模板查询数
                template_sql = """
                    SELECT COUNT(1) as count FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s AND req_info LIKE %s
                """
                template_result = self.execute_query(template_sql, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), '%###%'))
                template_count = template_result[0]['count'] if template_result else 0
                
                # 非模板查询数
                non_template_count = total_count - template_count
                
                results.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'total_count': total_count,
                    'template_count': template_count,
                    'non_template_count': non_template_count
                })
            
            return sorted(results, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"获取一周查询趋势失败: {e}")
            raise e

    def get_date_range_step_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的各环节耗时趋势"""
        try:
            # 如果没有指定日期范围，默认查询最近7天
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            if not start_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                start_date_obj = end_date_obj - timedelta(days=6)  # 包含今天共7天
                start_date = start_date_obj.strftime('%Y-%m-%d')
            
            # 计算日期范围
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            results = []
            current_date = start_date_obj
            
            while current_date <= end_date_obj:
                next_date = current_date + timedelta(days=1)
                
                for step_name, step_name_cn in self.step_name_mapping.items():
                    sql = f"""
                        SELECT AVG(cost) as avg_cost 
                        FROM t_step_time_record 
                        WHERE create_time >= %s AND create_time < %s 
                        AND step_name = %s
                    """
                    
                    # 对特定步骤添加额外条件
                    if step_name == 'QUERY_SCHEMA':
                        sql += """ AND biz_seq NOT IN (
                            SELECT biz_seq FROM t_handler_logs 
                            WHERE create_time >= %s AND create_time < %s 
                            AND req_info LIKE %s
                        ) AND cost > 1000"""
                        params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), step_name, current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), '%HIVE%')
                    elif step_name == 'SUB_QUERY':
                        sql += """ AND biz_seq NOT IN (
                            SELECT biz_seq FROM t_handler_logs 
                            WHERE create_time >= %s AND create_time < %s 
                            AND req_info LIKE %s
                        )"""
                        params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), step_name, current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), '%HIVE%')
                    else:
                        params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), step_name)
                    
                    result = self.execute_query(sql, params)
                    avg_cost = 0
                    if result and result[0]['avg_cost'] is not None:
                        avg_cost = round(float(result[0]['avg_cost']), 2)
                    
                    # 为每一天每个步骤都添加数据，没有数据时avg_cost为0
                    results.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'step_name': step_name,
                        'step_name_cn': step_name_cn,
                        'avg_cost': avg_cost
                    })
                
                current_date += timedelta(days=1)
            
            return sorted(results, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"获取日期范围步骤趋势失败: {e}")
            raise e

    def get_date_range_channel_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的各渠道查询趋势"""
        try:
            # 如果没有指定日期范围，默认查询最近7天
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            if not start_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                start_date_obj = end_date_obj - timedelta(days=6)  # 包含今天共7天
                start_date = start_date_obj.strftime('%Y-%m-%d')
            
            # 计算日期范围
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            results = []
            current_date = start_date_obj
            
            while current_date <= end_date_obj:
                next_date = current_date + timedelta(days=1)
                
                sql = """
                    SELECT channel, COUNT(1) as count 
                    FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    GROUP BY channel
                """
                channel_results = self.execute_query(sql, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')))
                
                # 创建渠道数据映射
                channel_data = {}
                for channel_result in channel_results:
                    channel = channel_result['channel'] or '未知渠道'
                    channel_data[channel] = channel_result['count']
                
                # 为所有已知渠道生成数据，没有数据的渠道count为0
                for channel, channel_name in self.channel_name_mapping.items():
                    count = channel_data.get(channel, 0)
                    results.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'channel': channel,
                        'channel_name': channel_name,
                        'count': count
                    })
                
                # 如果有未知渠道数据，也添加进去
                if '未知渠道' in channel_data:
                    results.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'channel': '未知渠道',
                        'channel_name': '未知渠道',
                        'count': channel_data['未知渠道']
                    })
                
                current_date += timedelta(days=1)
            
            return sorted(results, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"获取日期范围渠道趋势失败: {e}")
            raise e

    def get_weekly_step_trend(self, end_date: str) -> List[Dict[str, Any]]:
        """获取最近一周各环节的耗时趋势"""
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            results = []
            
            for i in range(7):
                current_date = end_date_obj - timedelta(days=i)
                next_date = current_date + timedelta(days=1)
                
                for step_name, step_name_cn in self.step_name_mapping.items():
                    sql = f"""
                        SELECT AVG(cost) as avg_cost 
                        FROM t_step_time_record 
                        WHERE create_time >= %s AND create_time < %s 
                        AND step_name = %s
                    """
                    
                    # 对特定步骤添加额外条件
                    if step_name == 'QUERY_SCHEMA':
                        sql += """ AND biz_seq NOT IN (
                            SELECT biz_seq FROM t_handler_logs 
                            WHERE create_time >= %s AND create_time < %s 
                            AND req_info LIKE %s
                        ) AND cost > 1000"""
                        params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), step_name, current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), '%HIVE%')
                    elif step_name == 'SUB_QUERY':
                        sql += """ AND biz_seq NOT IN (
                            SELECT biz_seq FROM t_handler_logs 
                            WHERE create_time >= %s AND create_time < %s 
                            AND req_info LIKE %s
                        )"""
                        params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), step_name, current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), '%HIVE%')
                    else:
                        params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d'), step_name)
                    
                    result = self.execute_query(sql, params)
                    if result and result[0]['avg_cost'] is not None:
                        results.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'step_name': step_name,
                            'step_name_cn': step_name_cn,
                            'avg_cost': round(result[0]['avg_cost'], 2)
                        })
            
            return sorted(results, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"获取一周步骤趋势失败: {e}")
            raise e

    def get_weekly_channel_trend(self, end_date: str) -> List[Dict[str, Any]]:
        """获取最近一周各渠道的查询趋势"""
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            results = []
            
            for i in range(7):
                current_date = end_date_obj - timedelta(days=i)
                next_date = current_date + timedelta(days=1)
                
                sql = """
                    SELECT channel, COUNT(1) as count 
                    FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    GROUP BY channel
                """
                channel_results = self.execute_query(sql, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')))
                
                for channel_result in channel_results:
                    channel = channel_result['channel'] or '未知渠道'
                    channel_name = self.channel_name_mapping.get(channel, channel)
                    results.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'channel': channel,
                        'channel_name': channel_name,
                        'count': channel_result['count']
                    })
            
            return sorted(results, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"获取一周渠道趋势失败: {e}")
            raise e

    def close(self):
        """关闭连接（SQLAlchemy不需要手动关闭连接池）"""
        # SQLAlchemy的连接池会自动管理连接
        pass
