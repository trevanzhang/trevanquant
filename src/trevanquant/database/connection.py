"""
数据库连接管理
提供数据库连接和会话管理功能
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str = None):
        """
        初始化数据库连接

        Args:
            database_url: 数据库连接URL，默认使用SQLite
        """
        if database_url is None:
            # 默认使用项目根目录下的database.db
            project_root = Path(__file__).parent.parent.parent.parent.parent
            db_path = project_root / "database.db"
            database_url = f"sqlite:///{db_path}"

        self.database_url = database_url

        # 创建引擎
        self.engine = create_engine(
            database_url,
            # SQLite配置
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,  # SQLite多线程支持
                "timeout": 30,  # 30秒超时
            },
            echo=False,  # 设置为True可以查看SQL语句
        )

        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # 创建所有表
        self.create_tables()

    def create_tables(self) -> None:
        """创建所有数据库表"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """删除所有数据库表（谨慎使用）"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        提供数据库会话的上下文管理器

        Example:
            with db.session_scope() as session:
                # 数据库操作
                pass
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_sql(self, sql: str) -> None:
        """执行SQL语句"""
        with self.session_scope() as session:
            session.execute(sql)


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db() -> Session:
    """
    获取数据库会话

    Returns:
        Session: 数据库会话对象
    """
    return db_manager.get_session()


def get_db_session() -> Generator[Session, None, None]:
    """
    获取数据库会话的生成器函数

    适用于FastAPI等框架的依赖注入

    Yields:
        Session: 数据库会话对象
    """
    session = get_db()
    try:
        yield session
    finally:
        session.close()


# 便捷函数
def with_session(func):
    """
    装饰器：自动管理数据库会话

    Example:
        @with_session
        def get_stock_by_code(session, stock_code: str):
            return session.query(Stock).filter(Stock.code == stock_code).first()
    """
    def wrapper(*args, **kwargs):
        with db_manager.session_scope() as session:
            return func(session, *args, **kwargs)
    return wrapper