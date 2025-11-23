# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseConfig:
    """数据库配置类"""
    def __init__(self):
        # 这里使用硬编码的配置，你可以根据需要修改为从配置文件读取
        self.db_user = 'root'
        self.db_password = 'pcc19940201'
        self.db_ip = 'localhost'
        self.db_port = 3306
        self.db_name = 'dqadeagent'

# 获取配置
db_config = DatabaseConfig()

# 对密码进行URL编码
encoded_password = quote_plus(db_config.db_password)

# 构建数据库连接URL，添加连接超时参数
DATABASE_URL = f"mysql+pymysql://{db_config.db_user}:{encoded_password}@{db_config.db_ip}:{db_config.db_port}/{db_config.db_name}?charset=utf8mb4&connect_timeout=5"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    pool_size=10, 
    max_overflow=20, 
    pool_recycle=3600, 
    echo=False, 
    pool_pre_ping=True,
    connect_args={
        'connect_timeout': 5,
        'read_timeout': 30,
        'write_timeout': 30
    }
)

def create_sqlalchemy_session():
    """创建SQLAlchemy会话"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sqlalchemy_session = SessionLocal()
    return sqlalchemy_session

def get_db_session():
    """获取数据库会话"""
    return create_sqlalchemy_session()

class MySqlDb:
    """数据库初始化类"""
    def __init__(self):
        self.engine = engine

    def init_db(self):
        """初始化数据库表"""
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化完成")

def first_init_db():
    """首次初始化数据库"""
    db = MySqlDb()
    db.init_db()
