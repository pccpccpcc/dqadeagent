# DQA德 Agent 后端服务

## 代码改造说明

本次代码改造完成了以下主要工作：

### 1. 数据库连接改造
- **原方案**: 使用 `aiomysql` 异步连接池
- **新方案**: 使用 `SQLAlchemy` + `PyMySQL` 同步连接

#### 核心文件
- `db_session.py`: 数据库会话管理模块，提供 `get_db_session()` 方法
- `database.py`: 改造后的 `DatabaseManager` 类，所有方法从异步改为同步

#### 使用示例
```python
from db_session import get_db_session
from sqlalchemy import text

def query_example():
    session = get_db_session()
    try:
        # 执行查询
        result = session.execute(
            text("SELECT * FROM table WHERE id = :id"), 
            {"id": 123}
        )
        records = result.fetchall()
        
        # 处理结果
        for record in records:
            print(record.column_name)
            
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        session.close()  # 重要：释放session
```

### 2. 服务层架构
- `data_service.py`: 数据服务类，封装所有业务逻辑
- `api_handlers.py`: API处理器类，包含所有HTTP请求的处理逻辑
- `app.py`: 应用入口，负责路由注册、中间件配置和应用启动

#### 架构层次
```
HTTP请求 → app.py (路由层) → api_handlers.py (处理器层) → data_service.py (服务层) → database.py (数据访问层) → db_session.py (会话管理)
```

### 3. API接口

启动服务：
```bash
cd backend
pip install -r requirements.txt
python app.py
```

服务将在 `http://localhost:8001` 启动

#### 主要接口

| 接口路径 | 方法 | 说明 | 参数 |
|---------|------|------|------|
| `/api/template-query/stats` | GET | 获取模板查询统计 | query_date |
| `/api/non-template-query/stats` | GET | 获取非模板查询统计 | query_date |
| `/api/template-query/errors` | GET | 获取模板查询错误统计 | query_date |
| `/api/non-template-query/errors` | GET | 获取非模板查询错误统计 | query_date |
| `/api/template-query/performance` | GET | 获取模板查询性能统计 | query_date |
| `/api/non-template-query/performance` | GET | 获取非模板查询性能统计 | query_date |
| `/api/step-performance` | GET | 获取各环节耗时统计 | query_date |
| `/api/channel-stats` | GET | 获取渠道查询统计 | query_date |
| `/api/no-ticket-stats` | GET | 获取免提单统计 | query_date |
| `/api/scenario-stats` | GET | 获取场景查询统计 | query_date |
| `/api/user-stats` | GET | 获取用户统计 | query_date |
| `/api/performance-detail` | GET | 获取性能详细分析 | biz_seq |
| `/api/query-trend` | GET | 获取查询趋势 | start_date, end_date |
| `/api/step-trend` | GET | 获取步骤趋势 | start_date, end_date |
| `/api/channel-trend` | GET | 获取渠道趋势 | start_date, end_date |

#### 接口示例
```bash
# 获取2024-01-01的模板查询统计
curl "http://localhost:8001/api/template-query/stats?query_date=2024-01-01"

# 获取性能详细分析
curl "http://localhost:8001/api/performance-detail?biz_seq=your_biz_seq"

# 获取查询趋势（7天）
curl "http://localhost:8001/api/query-trend?start_date=2024-01-01&end_date=2024-01-07"
```

### 4. 数据库配置

在 `db_session.py` 中修改数据库连接配置：

```python
class DatabaseConfig:
    def __init__(self):
        self.db_user = 'your_username'
        self.db_password = 'your_password' 
        self.db_ip = 'your_host'
        self.db_port = 3306
        self.db_name = 'your_database'
```

### 5. 示例：使用session进行批量查询

`data_service.py` 中包含了一个完整的示例 `DataEncryptService.decrypt_batch_values()`，展示了如何：
- 获取session
- 构建参数化查询
- 处理结果
- 异常处理
- 释放session

### 6. 依赖项

```txt
fastapi==0.104.1          # 原有依赖，保留兼容性
uvicorn[standard]==0.24.0 # 原有依赖
aiomysql==0.2.0          # 原有依赖  
pydantic==2.5.0          # 原有依赖
python-multipart==0.0.6  # 原有依赖
sqlalchemy==2.0.23       # 新增：SQLAlchemy ORM
pymysql==1.1.0           # 新增：MySQL驱动
aiohttp==3.9.1           # 新增：HTTP框架
cryptography==41.0.8     # 新增：加密支持
```

### 7. 注意事项

1. **Session管理**: 必须在 `finally` 块中调用 `session.close()` 释放连接
2. **异常处理**: 所有数据库操作都应该包含异常处理
3. **参数化查询**: 使用 SQLAlchemy 的 `text()` 和参数字典避免 SQL 注入
4. **连接池**: SQLAlchemy 自动管理连接池，无需手动管理
5. **日志**: 所有服务方法都包含了完整的错误日志

### 8. 迁移说明

- 原有的 `main.py` 使用 FastAPI，新的 `app.py` 使用 aiohttp
- 所有数据库方法从异步改为同步
- 保留了原有的错误码映射和业务逻辑
- API响应格式统一为 `{"data": result, "code": 200}` 或 `{"error": message, "code": error_code}`
