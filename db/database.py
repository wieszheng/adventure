# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/30 23:04
@Author   : wieszheng
@Software : PyCharm
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import settings

# 创建数据库引擎，用于连接数据库
engine = create_engine(
    settings.DATABASE_URL
)

# 创建数据库会话工厂，用于生成数据库会话对象
# autocommit=False: 禁用自动提交，需要手动提交事务
# autoflush=False: 禁用自动刷新，需要手动刷新数据到数据库
# bind=engine: 绑定到之前创建的数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明式基类，用于定义数据库模型
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数

    这是一个生成器函数，用于FastAPI的依赖注入系统。
    它提供数据库会话，并确保在使用完毕后正确关闭。

    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    创建所有数据库表

    根据定义的SQLAlchemy模型创建所有数据表。
    该函数应该在应用程序启动时调用一次。
    """
    Base.metadata.create_all(bind=engine)