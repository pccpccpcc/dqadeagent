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

    def _classify_error_code(self, result_code: str) -> str:
        """
        分类错误码为业务错误或系统错误
        返回: 'business' 或 'system'
        """
        if not result_code or result_code == '0000':
            return 'success'
        
        # 2.2.1 检查code是否为8位
        if len(result_code) != 8:
            return 'system'
        
        # 2.2.2 如果code前4位为B2DU
        if result_code[:4] == 'B2DU':
            # 读取第7位（索引6）
            if len(result_code) >= 7:
                seventh_char = result_code[6]
                if seventh_char in ['1', '2']:
                    return 'business'
            return 'system'
        
        # 2.2.3 如果code前4位为2030
        if result_code[:4] == '2030':
            # 读取后四位
            last_four = result_code[4:8]
            if last_four in ['1002', '1003', '1004', '1006', '1007', '1008', '1009']:
                return 'business'
            return 'system'
        
        # 2.2.4 其他情况归为系统错误
        return 'system'

    def get_overall_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """
        获取总体查询统计数据
        包括：总查询数、总成功数、总失败数、成功率
        """
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj + timedelta(days=1)
            
            # 1.1 总查询数
            total_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s
            """
            total_result = self.execute_query(total_sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            total_count = total_result[0]['count'] if total_result else 0
            
            # 1.2 总成功数
            success_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s AND result_code LIKE %s
            """
            success_result = self.execute_query(success_sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%0000%'))
            success_count = success_result[0]['count'] if success_result else 0
            
            # 1.3 总失败数
            failure_count = total_count - success_count
            
            # 成功率
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            return {
                'total_count': total_count,
                'success_count': success_count,
                'failure_count': failure_count,
                'success_rate': round(success_rate, 2),
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取总体查询统计数据失败: {e}")
            raise e

    def get_business_system_error_stats(self, queryDate: str) -> Dict[str, Any]:
        """
        获取业务错误和系统错误统计
        包括：业务错误数量、业务成功率、系统错误数量、系统成功率
        """
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj + timedelta(days=1)
            
            # 获取总查询数
            total_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s
            """
            total_result = self.execute_query(total_sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            total_count = total_result[0]['count'] if total_result else 0
            
            # 2.1 查出所有错误的code
            error_codes_sql = """
                SELECT result_code FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s AND result_code NOT LIKE %s
            """
            error_codes_result = self.execute_query(error_codes_sql, (queryDate, next_date.strftime('%Y-%m-%d'), '%0000%'))
            
            # 2.2 分类统计业务错误和系统错误
            business_error_count = 0
            system_error_count = 0
            
            for row in error_codes_result:
                result_code = row['result_code']
                error_type = self._classify_error_code(result_code)
                if error_type == 'business':
                    business_error_count += 1
                elif error_type == 'system':
                    system_error_count += 1
            
            # 2.3 计算业务成功率
            business_success_rate = (1 - business_error_count / total_count) * 100 if total_count > 0 else 0
            
            # 2.4 计算系统成功率
            system_success_rate = (1 - system_error_count / total_count) * 100 if total_count > 0 else 0
            
            return {
                'business_error_count': business_error_count,
                'business_success_rate': round(business_success_rate, 2),
                'system_error_count': system_error_count,
                'system_success_rate': round(system_success_rate, 2),
                'total_count': total_count,
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取业务系统错误统计失败: {e}")
            raise e

    def get_agent_subsystem_error_stats(self, queryDate: str) -> Dict[str, Any]:
        """
        获取agent子系统的错误统计
        包括：agent业务错误数量、业务成功率、系统错误数量、系统成功率
        """
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj + timedelta(days=1)
            
            # 获取总查询数
            total_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s
            """
            total_result = self.execute_query(total_sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            total_count = total_result[0]['count'] if total_result else 0
            
            # 3.1 查找agent子系统所有错误的code
            agent_error_codes_sql = """
                SELECT result_code FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND result_code NOT LIKE %s AND result_code LIKE %s
            """
            agent_error_codes_result = self.execute_query(
                agent_error_codes_sql, 
                (queryDate, next_date.strftime('%Y-%m-%d'), '%0000%', 'B2DU%')
            )
            
            # 3.2 分类统计agent子系统的业务错误和系统错误
            agent_business_error_count = 0
            agent_system_error_count = 0
            
            for row in agent_error_codes_result:
                result_code = row['result_code']
                # 读取第7位（索引6）
                if len(result_code) >= 7:
                    seventh_char = result_code[6]
                    if seventh_char in ['1', '2']:
                        agent_business_error_count += 1
                    else:
                        agent_system_error_count += 1
                else:
                    agent_system_error_count += 1
            
            # 3.3 计算agent子系统业务成功率
            agent_business_success_rate = (1 - agent_business_error_count / total_count) * 100 if total_count > 0 else 0
            
            # 3.4 计算agent子系统系统成功率
            agent_system_success_rate = (1 - agent_system_error_count / total_count) * 100 if total_count > 0 else 0
            
            return {
                'agent_business_error_count': agent_business_error_count,
                'agent_business_success_rate': round(agent_business_success_rate, 2),
                'agent_system_error_count': agent_system_error_count,
                'agent_system_success_rate': round(agent_system_success_rate, 2),
                'total_count': total_count,
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取agent子系统错误统计失败: {e}")
            raise e

    def get_ds_subsystem_error_stats(self, queryDate: str) -> Dict[str, Any]:
        """
        获取ds子系统的错误统计
        包括：ds业务错误数量、业务成功率、系统错误数量、系统成功率
        """
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj + timedelta(days=1)
            
            # 获取总查询数
            total_sql = """
                SELECT COUNT(1) as count FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s
            """
            total_result = self.execute_query(total_sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            total_count = total_result[0]['count'] if total_result else 0
            
            # 4.1 查找ds子系统所有错误的code
            ds_error_codes_sql = """
                SELECT result_code FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND result_code NOT LIKE %s AND result_code NOT LIKE %s
            """
            ds_error_codes_result = self.execute_query(
                ds_error_codes_sql, 
                (queryDate, next_date.strftime('%Y-%m-%d'), '%0000%', 'B2DU%')
            )
            
            # 4.2 分类统计ds子系统的业务错误和系统错误
            ds_business_error_count = 0
            ds_system_error_count = 0
            
            for row in ds_error_codes_result:
                result_code = row['result_code']
                # 4.2 如果code前4位为2030
                if len(result_code) >= 8 and result_code[:4] == '2030':
                    last_four = result_code[4:8]
                    if last_four in ['1002', '1003', '1004', '1006', '1007', '1008', '1009']:
                        ds_business_error_count += 1
                    else:
                        ds_system_error_count += 1
                else:
                    # 4.3 如果code前4位不为2030，统一认为系统错误
                    ds_system_error_count += 1
            
            # 4.4 计算ds子系统业务成功率
            ds_business_success_rate = (1 - ds_business_error_count / total_count) * 100 if total_count > 0 else 0
            
            # 4.5 计算ds子系统系统成功率
            ds_system_success_rate = (1 - ds_system_error_count / total_count) * 100 if total_count > 0 else 0
            
            return {
                'ds_business_error_count': ds_business_error_count,
                'ds_business_success_rate': round(ds_business_success_rate, 2),
                'ds_system_error_count': ds_system_error_count,
                'ds_system_success_rate': round(ds_system_success_rate, 2),
                'total_count': total_count,
                'queryDate': queryDate
            }
        except Exception as e:
            logger.error(f"获取ds子系统错误统计失败: {e}")
            raise e

    def get_template_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """
        获取综合查询统计数据（替换原来的模板查询统计）
        整合所有维度的统计数据
        """
        try:
            # 1. 总体统计
            overall_stats = self.get_overall_query_stats(queryDate)
            
            # 2. 业务/系统错误统计
            business_system_stats = self.get_business_system_error_stats(queryDate)
            
            # 3. agent子系统统计
            agent_stats = self.get_agent_subsystem_error_stats(queryDate)
            
            # 4. ds子系统统计
            ds_stats = self.get_ds_subsystem_error_stats(queryDate)
            
            # 整合所有统计数据
            return {
                **overall_stats,
                **business_system_stats,
                **agent_stats,
                **ds_stats
            }
        except Exception as e:
            logger.error(f"获取综合查询统计数据失败: {e}")
            raise e

    def get_non_template_query_stats(self, queryDate: str) -> Dict[str, Any]:
        """
        保留此方法以兼容现有API，返回与template_query_stats相同的数据
        """
        return self.get_template_query_stats(queryDate)

    def _calculate_p90(self, costs: List[float]) -> float:
        """计算P90值 - 使用线性插值方法"""
        if not costs:
            return 0
        if len(costs) == 1:
            return costs[0]
        
        sorted_costs = sorted(costs)
        n = len(sorted_costs)
        
        # P90的位置：0.9 * (n - 1)，这样P100就是最后一个元素
        position = 0.9 * (n - 1)
        lower_index = int(position)
        upper_index = min(lower_index + 1, n - 1)
        
        # 如果position是整数，直接返回该位置的值
        if position == lower_index:
            return sorted_costs[lower_index]
        
        # 否则进行线性插值
        weight = position - lower_index
        return sorted_costs[lower_index] * (1 - weight) + sorted_costs[upper_index] * weight
    
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
                # 先获取平均值和最大值
                result = self.execute_query(query_info['sql'], query_info['params'])
                if result and result[0]['avg_cost'] is not None:
                    # 获取所有cost值用于计算P90
                    all_costs_sql = query_info['sql'].replace(
                        'SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost',
                        'SELECT cost'
                    )
                    all_costs_result = self.execute_query(all_costs_sql, query_info['params'])
                    costs = [float(row['cost']) for row in all_costs_result if row.get('cost')]
                    p90_cost = self._calculate_p90(costs) if costs else 0
                    
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
                        'p90_cost': round(p90_cost, 2),
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
                # 先获取平均值和最大值
                result = self.execute_query(query_info['sql'], query_info['params'])
                if result and result[0]['avg_cost'] is not None:
                    # 获取所有cost值用于计算P90
                    all_costs_sql = query_info['sql'].replace(
                        'SELECT AVG(cost) as avg_cost, MAX(cost) as max_cost',
                        'SELECT cost'
                    )
                    all_costs_result = self.execute_query(all_costs_sql, query_info['params'])
                    costs = [float(row['cost']) for row in all_costs_result if row.get('cost')]
                    p90_cost = self._calculate_p90(costs) if costs else 0
                    
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
                        'p90_cost': round(p90_cost, 2),
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
                # 获取所有cost数据用于计算P90
                cost_sql = f"""
                    SELECT cost 
                    FROM t_step_time_record 
                    WHERE create_time >= %s AND create_time < %s 
                    AND step_name = %s
                """
                
                # 对特定步骤添加额外条件
                if step_name == 'QUERY_SCHEMA':
                    cost_sql += """ AND biz_seq NOT IN (
                        SELECT biz_seq FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND req_info LIKE %s
                    ) AND cost > 1000"""
                    params = (queryDate, next_date.strftime('%Y-%m-%d'), step_name, queryDate, next_date.strftime('%Y-%m-%d'), '%HIVE%')
                elif step_name == 'SUB_QUERY':
                    cost_sql += """ AND biz_seq NOT IN (
                        SELECT biz_seq FROM t_handler_logs 
                        WHERE create_time >= %s AND create_time < %s 
                        AND req_info LIKE %s
                    )"""
                    params = (queryDate, next_date.strftime('%Y-%m-%d'), step_name, queryDate, next_date.strftime('%Y-%m-%d'), '%HIVE%')
                else:
                    params = (queryDate, next_date.strftime('%Y-%m-%d'), step_name)
                
                cost_results = self.execute_query(cost_sql, params)
                
                if cost_results and len(cost_results) > 0:
                    from decimal import Decimal
                    
                    # 提取所有cost值
                    costs = [float(row['cost']) if isinstance(row['cost'], Decimal) else row['cost'] 
                            for row in cost_results if row['cost'] is not None]
                    
                    if costs:
                        # 计算平均值、最大值和P90
                        avg_cost = sum(costs) / len(costs)
                        max_cost = max(costs)
                        p90_cost = self._calculate_p90(costs)
                        
                        results.append({
                            'step_name': step_name,
                            'step_name_cn': step_name_cn,
                            'avg_cost': round(avg_cost, 2),
                            'p90_cost': round(p90_cost, 2),
                            'max_cost': round(max_cost, 2)
                        })
            
            return results
        except Exception as e:
            logger.error(f"获取步骤性能统计失败: {e}")
            raise e

    def get_channel_stats(self, queryDate: str) -> Dict[str, Any]:
        """获取各个渠道的查询数量统计（按项目组成员和非项目组成员划分）"""
        try:
            date_obj = datetime.strptime(queryDate, '%Y-%m-%d').date()
            next_date = date_obj.replace(day=date_obj.day + 1) if date_obj.day < 28 else date_obj.replace(month=date_obj.month + 1, day=1)
            
            # 项目组成员列表
            project_members = [
                'qingyiluan', 'ruihu', 'syroalxiao', 'froggynie', 'xinxu', 'kuixu', 
                'liamyang', 'owenzhang', 'xinyinshu', 'weijiang', 'taojiang', 'eruditemao',
                'dylanding', 'hongqinluo', 'mjyu', 'docwang', 'bowenduan', 'alexxliu',
                'ivesxiong', 'xiweili', 'derekye', 'rawlinschen', 'tiantianhu', 'haoqunliu',
                'penhuazhang', 'liangdonghu', 'rorozhang', 'quanzhang', 'pengfeili', 'kellymeng',
                'qianlong', 'kaipengxu', 'norazeng', 'colinxu', 'xiaojianxia', 'joeyxu',
                'rouzhitang', 'cccpeng', 'jiajian'
            ]
            
            # 查询项目组成员的渠道统计
            sql_members = """
                SELECT channel, COUNT(1) as count 
                FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND user_id IN ({})
                GROUP BY channel
            """.format(','.join(['%s'] * len(project_members)))
            
            params_members = [queryDate, next_date.strftime('%Y-%m-%d')] + project_members
            results_members = self.execute_query(sql_members, tuple(params_members))
            
            # 查询非项目组成员的渠道统计
            sql_non_members = """
                SELECT channel, COUNT(1) as count 
                FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s 
                AND (user_id NOT IN ({}) OR user_id IS NULL)
                GROUP BY channel
            """.format(','.join(['%s'] * len(project_members)))
            
            params_non_members = [queryDate, next_date.strftime('%Y-%m-%d')] + project_members
            results_non_members = self.execute_query(sql_non_members, tuple(params_non_members))
            
            # 格式化项目组成员数据
            member_stats = []
            for result in results_members:
                channel = result['channel'] or '未知渠道'
                channel_name = self.channel_name_mapping.get(channel, channel)
                member_stats.append({
                    'channel': channel,
                    'channel_name': channel_name,
                    'count': result['count']
                })
            
            # 格式化非项目组成员数据
            non_member_stats = []
            for result in results_non_members:
                channel = result['channel'] or '未知渠道'
                channel_name = self.channel_name_mapping.get(channel, channel)
                non_member_stats.append({
                    'channel': channel,
                    'channel_name': channel_name,
                    'count': result['count']
                })
            
            return {
                'member_stats': sorted(member_stats, key=lambda x: x['count'], reverse=True),
                'non_member_stats': sorted(non_member_stats, key=lambda x: x['count'], reverse=True)
            }
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
            
            # 项目组成员列表
            project_members = [
                'qingyiluan', 'ruihu', 'syroalxiao', 'froggynie', 'xinxu', 'kuixu', 
                'liamyang', 'owenzhang', 'xinyinshu', 'weijiang', 'taojiang', 'eruditemao',
                'dylanding', 'hongqinluo', 'mjyu', 'docwang', 'bowenduan', 'alexxliu',
                'ivesxiong', 'xiweili', 'derekye', 'rawlinschen', 'tiantianhu', 'haoqunliu',
                'penhuazhang', 'liangdonghu', 'rorozhang', 'quanzhang', 'pengfeili', 'kellymeng',
                'qianlong', 'kaipengxu', 'norazeng', 'colinxu', 'xiaojianxia', 'joeyxu',
                'rouzhitang', 'cccpeng', 'jiajian'
            ]
            
            results = []
            for query_info in scenario_queries:
                # 总体查询
                result = self.execute_query(query_info['sql'], query_info['params'])
                total_count = result[0]['count'] if result else 0
                
                # 项目组成员查询
                member_sql = query_info['sql'].replace(
                    'WHERE create_time',
                    'WHERE user_id IN ({}) AND create_time'.format(','.join(['%s'] * len(project_members)))
                )
                member_params = list(project_members) + list(query_info['params'])
                member_result = self.execute_query(member_sql, tuple(member_params))
                member_count = member_result[0]['count'] if member_result else 0
                
                # 非项目组成员查询
                non_member_sql = query_info['sql'].replace(
                    'WHERE create_time',
                    'WHERE (user_id NOT IN ({}) OR user_id IS NULL) AND create_time'.format(','.join(['%s'] * len(project_members)))
                )
                non_member_params = list(project_members) + list(query_info['params'])
                non_member_result = self.execute_query(non_member_sql, tuple(non_member_params))
                non_member_count = non_member_result[0]['count'] if non_member_result else 0
                
                results.append({
                    'scenario': query_info['scenario'],
                    'scenario_name': query_info['scenario_name'],
                    'count': total_count,
                    'member_count': member_count,
                    'non_member_count': non_member_count
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
            # 1. 获取req_info（用户请求信息）
            req_info_sql = """
                SELECT req_info FROM t_handler_logs 
                WHERE biz_seq = %s 
                LIMIT 1
            """
            req_info_result = self.execute_query(req_info_sql, (biz_seq,))
            req_info = req_info_result[0]['req_info'] if req_info_result else None
            
            # 2. 获取步骤详情（排除REQ_DS步骤）
            steps_sql = """
                SELECT step_name, sub_step_name, cost 
                FROM t_step_time_record 
                WHERE biz_seq = %s 
                AND sub_step_name != 'REQ_DS'
                ORDER BY create_time
            """
            steps_result = self.execute_query(steps_sql, (biz_seq,))
            
            steps = []
            total_cost = 0
            
            for step in steps_result:
                steps.append({
                    'step_name': step['step_name'],
                    'sub_step_name': step['sub_step_name'],
                    'cost': step['cost'],
                    'step_name_cn': self.step_name_mapping.get(step['step_name'], step['step_name'])
                })
                total_cost += step['cost']
            
            # 3. 获取SQL执行详情（按create_time排序）
            sql_details_sql = """
                SELECT sql_str, query_time, sql_execute_time, create_time
                FROM query_sql_log 
                WHERE biz_seq = %s
                ORDER BY create_time
            """
            sql_details_result = self.execute_query(sql_details_sql, (biz_seq,))
            
            sql_details = []
            for row in sql_details_result:
                sql_details.append({
                    'sql_str': row.get('sql_str'),
                    'query_time': row.get('query_time'),
                    'sql_execute_time': row.get('sql_execute_time'),
                    'create_time': row.get('create_time').strftime('%Y-%m-%d %H:%M:%S') if row.get('create_time') else None
                })
            
            return {
                'biz_seq': biz_seq,
                'req_info': req_info,
                'total_cost': total_cost,
                'steps': steps,
                'sql_details': sql_details
            }
        except Exception as e:
            logger.error(f"获取性能详细分析失败: {e}")
            raise e

    def get_date_range_query_trend(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """获取指定日期范围的查询趋势（按项目组和非项目组划分）"""
        try:
            # 项目组成员列表
            project_members = [
                'qingyiluan', 'ruihu', 'syroalxiao', 'froggynie', 'xinxu', 'kuixu', 
                'liamyang', 'owenzhang', 'xinyinshu', 'weijiang', 'taojiang', 'eruditemao',
                'dylanding', 'hongqinluo', 'mjyu', 'docwang', 'bowenduan', 'alexxliu',
                'ivesxiong', 'xiweili', 'derekye', 'rawlinschen', 'tiantianhu', 'haoqunliu',
                'penhuazhang', 'liangdonghu', 'rorozhang', 'quanzhang', 'pengfeili', 'kellymeng',
                'qianlong', 'kaipengxu', 'norazeng', 'colinxu', 'xiaojianxia', 'joeyxu',
                'rouzhitang', 'cccpeng', 'jiajian'
            ]
            
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
                
                # 项目组查询数
                member_sql = """
                    SELECT COUNT(1) as count FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    AND user_id IN ({})
                """.format(','.join(['%s'] * len(project_members)))
                member_params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')) + tuple(project_members)
                member_result = self.execute_query(member_sql, member_params)
                member_count = member_result[0]['count'] if member_result else 0
                
                # 非项目组查询数
                non_member_sql = """
                    SELECT COUNT(1) as count FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    AND (user_id NOT IN ({}) OR user_id IS NULL)
                """.format(','.join(['%s'] * len(project_members)))
                non_member_params = (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')) + tuple(project_members)
                non_member_result = self.execute_query(non_member_sql, non_member_params)
                non_member_count = non_member_result[0]['count'] if non_member_result else 0
                
                results.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'total_count': total_count,
                    'member_count': member_count,
                    'non_member_count': non_member_count
                })
                
                current_date += timedelta(days=1)
            
            return results
        except Exception as e:
            logger.error(f"获取日期范围查询趋势失败: {e}")
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
        """获取指定日期范围的各渠道查询趋势（包含项目组和非项目组维度）"""
        try:
            project_members = [
                'qingyiluan', 'ruihu', 'syroalxiao', 'froggynie', 'xinxu', 'kuixu',
                'liamyang', 'owenzhang', 'xinyinshu', 'weijiang', 'taojiang', 'eruditemao',
                'dylanding', 'hongqinluo', 'mjyu', 'docwang', 'bowenduan', 'alexxliu',
                'ivesxiong', 'xiweili', 'derekye', 'rawlinschen', 'tiantianhu', 'haoqunliu',
                'penhuazhang', 'liangdonghu', 'rorozhang', 'quanzhang', 'pengfeili', 'kellymeng',
                'qianlong', 'kaipengxu', 'norazeng', 'colinxu', 'xiaojianxia', 'joeyxu',
                'rouzhitang', 'cccpeng', 'jiajian'
            ]
            
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
                
                # 总查询数（按渠道）
                sql_total = """
                    SELECT channel, COUNT(1) as count 
                    FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    GROUP BY channel
                """
                total_results = self.execute_query(sql_total, (current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')))
                
                # 项目组查询数（按渠道）
                sql_member = f"""
                    SELECT channel, COUNT(1) as count 
                    FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    AND user_id IN ({', '.join(['%s'] * len(project_members))})
                    GROUP BY channel
                """
                member_params = [current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')] + project_members
                member_results = self.execute_query(sql_member, tuple(member_params))
                
                # 非项目组查询数（按渠道）
                sql_non_member = f"""
                    SELECT channel, COUNT(1) as count 
                    FROM t_handler_logs 
                    WHERE create_time >= %s AND create_time < %s 
                    AND (user_id NOT IN ({', '.join(['%s'] * len(project_members))}) OR user_id IS NULL)
                    GROUP BY channel
                """
                non_member_params = [current_date.strftime('%Y-%m-%d'), next_date.strftime('%Y-%m-%d')] + project_members
                non_member_results = self.execute_query(sql_non_member, tuple(non_member_params))
                
                # 创建渠道数据映射
                channel_data = {}
                member_data = {}
                non_member_data = {}
                
                # 处理总数
                for result in total_results:
                    channel = result['channel'] or '未知渠道'
                    channel_data[channel] = result['count']
                
                # 处理项目组数据
                for result in member_results:
                    channel = result['channel'] or '未知渠道'
                    member_data[channel] = result['count']
                
                # 处理非项目组数据
                for result in non_member_results:
                    channel = result['channel'] or '未知渠道'
                    non_member_data[channel] = result['count']
                
                # 为所有已知渠道生成数据，没有数据的渠道count为0
                for channel, channel_name in self.channel_name_mapping.items():
                    results.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'channel': channel,
                        'channel_name': channel_name,
                        'count': channel_data.get(channel, 0),
                        'member_count': member_data.get(channel, 0),
                        'non_member_count': non_member_data.get(channel, 0)
                    })
                
                # 如果有未知渠道数据，也添加进去
                if '未知渠道' in channel_data:
                    results.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'channel': '未知渠道',
                        'channel_name': '未知渠道',
                        'count': channel_data.get('未知渠道', 0),
                        'member_count': member_data.get('未知渠道', 0),
                        'non_member_count': non_member_data.get('未知渠道', 0)
                    })
                
                current_date += timedelta(days=1)
            
            return sorted(results, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"获取日期范围渠道趋势失败: {e}")
            raise e

    def get_agent_error_details(self, queryDate: str) -> Dict[str, Any]:
        """获取Agent子系统错误明细数据 - 三层结构"""
        try:
            next_date = datetime.strptime(queryDate, '%Y-%m-%d') + timedelta(days=1)
            
            # 获取所有Agent错误记录
            sql = """
                SELECT biz_seq, result_code, req_info, rsp_info, create_time
                FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s
                AND result_code NOT LIKE '%%0000' 
                AND result_code LIKE 'B2DU%%'
                ORDER BY create_time DESC
            """
            
            results = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            
            # 错误类型映射
            business_error_types = {
                '1': '用户输入信息缺失/错误',
                '2': '用户权限问题'
            }
            
            system_error_types = {
                '3': '服务调用错误',
                '4': '数据访问错误',
                '9': '服务端发生了未预期的内部异常'
            }
            
            # 分类统计
            business_errors = {}
            system_errors = {}
            
            for record in results:
                result_code = record.get('result_code', '')
                if len(result_code) >= 7:
                    error_type = result_code[6]  # 第7位（索引6）
                    last_four = result_code[-4:]  # 后四位
                    
                    error_data = {
                        'biz_seq': record.get('biz_seq'),
                        'result_code': result_code,
                        'req_info': record.get('req_info'),
                        'rsp_info': record.get('rsp_info'),
                        'create_time': record.get('create_time').strftime('%Y-%m-%d %H:%M:%S') if record.get('create_time') else None
                    }
                    
                    # 判断是业务错误还是系统错误
                    if error_type in ['1', '2']:
                        # 业务错误
                        if error_type not in business_errors:
                            business_errors[error_type] = {
                                'type_name': business_error_types.get(error_type, f'未知错误类型{error_type}'),
                                'count': 0,
                                'code_groups': {}
                            }
                        
                        business_errors[error_type]['count'] += 1
                        
                        if last_four not in business_errors[error_type]['code_groups']:
                            business_errors[error_type]['code_groups'][last_four] = {
                                'code': last_four,
                                'count': 0,
                                'details': []
                            }
                        
                        business_errors[error_type]['code_groups'][last_four]['count'] += 1
                        business_errors[error_type]['code_groups'][last_four]['details'].append(error_data)
                    else:
                        # 系统错误
                        if error_type not in system_errors:
                            system_errors[error_type] = {
                                'type_name': system_error_types.get(error_type, f'未知错误类型{error_type}'),
                                'count': 0,
                                'code_groups': {}
                            }
                        
                        system_errors[error_type]['count'] += 1
                        
                        if last_four not in system_errors[error_type]['code_groups']:
                            system_errors[error_type]['code_groups'][last_four] = {
                                'code': last_four,
                                'count': 0,
                                'details': []
                            }
                        
                        system_errors[error_type]['code_groups'][last_four]['count'] += 1
                        system_errors[error_type]['code_groups'][last_four]['details'].append(error_data)
            
            # 转换为列表格式
            business_error_list = [
                {
                    'error_type': key,
                    'type_name': value['type_name'],
                    'count': value['count'],
                    'code_groups': list(value['code_groups'].values())
                }
                for key, value in business_errors.items()
            ]
            
            system_error_list = [
                {
                    'error_type': key,
                    'type_name': value['type_name'],
                    'count': value['count'],
                    'code_groups': list(value['code_groups'].values())
                }
                for key, value in system_errors.items()
            ]
            
            return {
                'queryDate': queryDate,
                'business_errors': business_error_list,
                'system_errors': system_error_list,
                'total_business_count': sum(e['count'] for e in business_error_list),
                'total_system_count': sum(e['count'] for e in system_error_list)
            }
            
        except Exception as e:
            logger.error(f"获取Agent错误明细失败: {e}")
            raise e
    
    def get_ds_error_details(self, queryDate: str) -> Dict[str, Any]:
        """获取DS子系统错误明细数据"""
        try:
            next_date = datetime.strptime(queryDate, '%Y-%m-%d') + timedelta(days=1)
            
            # 获取所有DS错误记录
            sql = """
                SELECT biz_seq, result_code, req_info, rsp_info, create_time
                FROM t_handler_logs 
                WHERE create_time >= %s AND create_time < %s
                AND result_code NOT LIKE '%%0000' 
                AND result_code LIKE 'B2DS%%'
                ORDER BY create_time DESC
            """
            
            results = self.execute_query(sql, (queryDate, next_date.strftime('%Y-%m-%d')))
            
            # DS的业务错误码映射（与Agent相同）
            business_error_codes = {
                '1002': '用户没有对应子系统权限',
                '1003': 'dbName输入错误',
                '1004': 'DCN信息为空，请排查子系统是否接入AOMP',
                '1006': 'DCN不为异地备',
                '1007': 'dcn输入错误',
                '1008': '查询出的IDC信息为空，请排查子系统是否接入AOMP',
                '1009': 'IDC输入错误',
                '2001': '提交SQL执行异常',
                '2002': '解析sql中的表名发送异常'
            }
            
            # DS的系统错误码映射
            system_error_codes = {
                '3001': 'AOMP返回结果为空',
                '3002': 'SQL执行超时'
            }
            
            # 分类统计
            business_errors = {}
            system_errors = {}
            
            for record in results:
                result_code = record.get('result_code', '')
                if len(result_code) >= 7:
                    error_type = result_code[6]  # 第7位（索引6）
                    last_four = result_code[-4:]  # 后四位
                    
                    error_data = {
                        'biz_seq': record.get('biz_seq'),
                        'result_code': result_code,
                        'req_info': record.get('req_info'),
                        'rsp_info': record.get('rsp_info'),
                        'create_time': record.get('create_time').strftime('%Y-%m-%d %H:%M:%S') if record.get('create_time') else None
                    }
                    
                    # 判断是业务错误还是系统错误
                    if error_type in ['1', '2']:
                        # 业务错误 - 直接按后四位分组
                        if last_four not in business_errors:
                            business_errors[last_four] = {
                                'code': last_four,
                                'code_name': business_error_codes.get(last_four, f'未知错误码{last_four}'),
                                'count': 0,
                                'details': []
                            }
                        
                        business_errors[last_four]['count'] += 1
                        business_errors[last_four]['details'].append(error_data)
                    else:
                        # 系统错误 - 直接按后四位分组
                        # 如果不是3001和3002，也不在业务错误码里面，归类为"其他"
                        if last_four in system_error_codes:
                            code_key = last_four
                            code_name = system_error_codes[last_four]
                        elif last_four not in business_error_codes:
                            code_key = '9999'  # 其他
                            code_name = '其他'
                        else:
                            code_key = last_four
                            code_name = f'错误码{last_four}'
                        
                        if code_key not in system_errors:
                            system_errors[code_key] = {
                                'code': code_key,
                                'code_name': code_name,
                                'count': 0,
                                'details': []
                            }
                        
                        system_errors[code_key]['count'] += 1
                        system_errors[code_key]['details'].append(error_data)
            
            # 转换为列表格式并排序
            business_error_list = sorted(
                list(business_errors.values()),
                key=lambda x: x['count'],
                reverse=True
            )
            
            system_error_list = sorted(
                list(system_errors.values()),
                key=lambda x: x['count'],
                reverse=True
            )
            
            return {
                'queryDate': queryDate,
                'business_errors': business_error_list,
                'system_errors': system_error_list,
                'total_business_count': sum(e['count'] for e in business_error_list),
                'total_system_count': sum(e['count'] for e in system_error_list)
            }
            
        except Exception as e:
            logger.error(f"获取DS错误明细失败: {e}")
            raise e

    def close(self):
        """关闭连接（SQLAlchemy不需要手动关闭连接池）"""
        # SQLAlchemy的连接池会自动管理连接
        pass
