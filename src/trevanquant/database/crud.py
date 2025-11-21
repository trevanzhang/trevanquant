"""
数据库CRUD操作
提供基础的数据库增删改查操作
"""

from datetime import datetime, date
from typing import List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from .models import (
    Stock, DailyData, TechnicalIndicator,
    MarketIndex, AnalysisResult, DataUpdateLog
)
from .connection import db_manager

# 泛型类型变量
T = TypeVar('T')


class BaseCRUD(Generic[T]):
    """基础CRUD操作类"""

    def __init__(self, model: Type[T]):
        """
        初始化CRUD操作类

        Args:
            model: 数据库模型类
        """
        self.model = model

    def create(self, session: Session, obj_data: dict) -> T:
        """
        创建记录

        Args:
            session: 数据库会话
            obj_data: 要创建的数据字典

        Returns:
            T: 创建的记录对象
        """
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def create_batch(self, session: Session, objects_data: List[dict]) -> List[T]:
        """
        批量创建记录

        Args:
            session: 数据库会话
            objects_data: 要创建的数据字典列表

        Returns:
            List[T]: 创建的记录对象列表
        """
        db_objects = [self.model(**obj_data) for obj_data in objects_data]
        session.add_all(db_objects)
        session.commit()
        return db_objects

    def get(self, session: Session, id: int) -> Optional[T]:
        """
        根据ID获取记录

        Args:
            session: 数据库会话
            id: 记录ID

        Returns:
            Optional[T]: 记录对象或None
        """
        return session.query(self.model).filter(self.model.id == id).first()

    def get_by_field(self, session: Session, field_name: str, value) -> Optional[T]:
        """
        根据字段值获取记录

        Args:
            session: 数据库会话
            field_name: 字段名
            value: 字段值

        Returns:
            Optional[T]: 记录对象或None
        """
        field = getattr(self.model, field_name)
        return session.query(self.model).filter(field == value).first()

    def get_multi(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        descending: bool = False
    ) -> List[T]:
        """
        获取多条记录

        Args:
            session: 数据库会话
            skip: 跳过的记录数
            limit: 返回的记录数限制
            order_by: 排序字段
            descending: 是否降序

        Returns:
            List[T]: 记录对象列表
        """
        query = session.query(self.model)

        # 排序
        if order_by:
            field = getattr(self.model, order_by)
            if descending:
                query = query.order_by(desc(field))
            else:
                query = query.order_by(asc(field))

        return query.offset(skip).limit(limit).all()

    def update(
        self,
        session: Session,
        db_obj: T,
        obj_data: dict
    ) -> T:
        """
        更新记录

        Args:
            session: 数据库会话
            db_obj: 要更新的记录对象
            obj_data: 更新数据字典

        Returns:
            T: 更新后的记录对象
        """
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # 自动更新时间戳（如果模型有updated_at字段）
        if hasattr(db_obj, 'updated_at'):
            db_obj.updated_at = datetime.now()

        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, db_obj: T) -> T:
        """
        删除记录

        Args:
            session: 数据库会话
            db_obj: 要删除的记录对象

        Returns:
            T: 被删除的记录对象
        """
        session.delete(db_obj)
        session.commit()
        return db_obj

    def count(self, session: Session) -> int:
        """
        获取记录总数

        Args:
            session: 数据库会话

        Returns:
            int: 记录总数
        """
        return session.query(self.model).count()


class StockCRUD(BaseCRUD[Stock]):
    """股票信息CRUD操作"""

    def get_by_code(self, session: Session, code: str) -> Optional[Stock]:
        """根据股票代码获取股票信息"""
        return self.get_by_field(session, 'code', code)

    def get_by_market(self, session: Session, market: str) -> List[Stock]:
        """根据市场获取股票列表"""
        return session.query(self.model).filter(self.model.market == market).all()

    def get_active_stocks(self, session: Session) -> List[Stock]:
        """获取活跃股票（未退市）"""
        return session.query(self.model).filter(
            and_(
                self.model.is_delisted == False,
                self.model.is_st == False
            )
        ).all()

    def create_or_update(self, session: Session, stock_data: dict) -> Stock:
        """创建或更新股票信息"""
        stock = self.get_by_code(session, stock_data['code'])
        if stock:
            return self.update(session, stock, stock_data)
        else:
            return self.create(session, stock_data)


class DailyDataCRUD(BaseCRUD[DailyData]):
    """日线数据CRUD操作"""

    def get_by_stock_and_date(
        self,
        session: Session,
        stock_code: str,
        trade_date: date
    ) -> Optional[DailyData]:
        """根据股票代码和交易日期获取日线数据"""
        return session.query(self.model).filter(
            and_(
                self.model.stock_code == stock_code,
                self.model.trade_date == trade_date
            )
        ).first()

    def get_by_stock(
        self,
        session: Session,
        stock_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = None
    ) -> List[DailyData]:
        """根据股票代码获取日线数据"""
        query = session.query(self.model).filter(self.model.stock_code == stock_code)

        if start_date:
            query = query.filter(self.model.trade_date >= start_date)
        if end_date:
            query = query.filter(self.model.trade_date <= end_date)

        query = query.order_by(desc(self.model.trade_date))

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_latest_date(self, session: Session, stock_code: str) -> Optional[date]:
        """获取股票最新交易日期"""
        result = session.query(self.model.trade_date).filter(
            self.model.stock_code == stock_code
        ).order_by(desc(self.model.trade_date)).first()

        return result.trade_date if result else None

    def batch_upsert(self, session: Session, data_list: List[dict]) -> List[DailyData]:
        """批量插入或更新日线数据"""
        result = []
        for data in data_list:
            existing = self.get_by_stock_and_date(
                session, data['stock_code'], data['trade_date']
            )
            if existing:
                updated = self.update(session, existing, data)
                result.append(updated)
            else:
                created = self.create(session, data)
                result.append(created)
        return result


class TechnicalIndicatorCRUD(BaseCRUD[TechnicalIndicator]):
    """技术指标CRUD操作"""

    def get_by_stock_and_type(
        self,
        session: Session,
        stock_code: str,
        indicator_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TechnicalIndicator]:
        """根据股票代码和指标类型获取技术指标数据"""
        query = session.query(self.model).filter(
            and_(
                self.model.stock_code == stock_code,
                self.model.indicator_type == indicator_type
            )
        )

        if start_date:
            query = query.filter(self.model.trade_date >= start_date)
        if end_date:
            query = query.filter(self.model.trade_date <= end_date)

        return query.order_by(desc(self.model.trade_date)).all()

    def delete_by_stock_and_date_range(
        self,
        session: Session,
        stock_code: str,
        start_date: date,
        end_date: date
    ) -> int:
        """删除指定股票和时间范围的技术指标"""
        count = session.query(self.model).filter(
            and_(
                self.model.stock_code == stock_code,
                self.model.trade_date >= start_date,
                self.model.trade_date <= end_date
            )
        ).delete()
        session.commit()
        return count


class MarketIndexCRUD(BaseCRUD[MarketIndex]):
    """市场指数CRUD操作"""

    def get_by_code_and_date(
        self,
        session: Session,
        index_code: str,
        trade_date: date
    ) -> Optional[MarketIndex]:
        """根据指数代码和日期获取指数数据"""
        return session.query(self.model).filter(
            and_(
                self.model.index_code == index_code,
                self.model.trade_date == trade_date
            )
        ).first()

    def get_latest_by_code(self, session: Session, index_code: str) -> Optional[MarketIndex]:
        """获取指定指数的最新数据"""
        return session.query(self.model).filter(
            self.model.index_code == index_code
        ).order_by(desc(self.model.trade_date)).first()


class AnalysisResultCRUD(BaseCRUD[AnalysisResult]):
    """分析结果CRUD操作"""

    def get_by_stock_and_strategy(
        self,
        session: Session,
        stock_code: str,
        strategy_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AnalysisResult]:
        """根据股票代码和策略获取分析结果"""
        query = session.query(self.model).filter(
            and_(
                self.model.stock_code == stock_code,
                self.model.strategy_name == strategy_name
            )
        )

        if start_date:
            query = query.filter(self.model.trade_date >= start_date)
        if end_date:
            query = query.filter(self.model.trade_date <= end_date)

        return query.order_by(desc(self.model.trade_date)).all()

    def get_buy_signals(
        self,
        session: Session,
        trade_date: date,
        min_confidence: float = 0.5
    ) -> List[AnalysisResult]:
        """获取指定日期的买入信号"""
        return session.query(self.model).filter(
            and_(
                self.model.trade_date == trade_date,
                self.model.signal == 'BUY',
                self.model.confidence >= min_confidence
            )
        ).all()


class DataUpdateLogCRUD(BaseCRUD[DataUpdateLog]):
    """数据更新日志CRUD操作"""

    def get_latest_by_type(
        self,
        session: Session,
        data_type: str
    ) -> Optional[DataUpdateLog]:
        """获取指定数据类型的最新更新日志"""
        return session.query(self.model).filter(
            self.model.data_type == data_type
        ).order_by(desc(self.model.created_at)).first()

    def create_log(
        self,
        session: Session,
        data_type: str,
        status: str = "RUNNING"
    ) -> DataUpdateLog:
        """创建更新日志"""
        log_data = {
            'data_type': data_type,
            'start_time': datetime.now(),
            'status': status
        }
        return self.create(session, log_data)


# 创建CRUD实例
stock_crud = StockCRUD(Stock)
daily_data_crud = DailyDataCRUD(DailyData)
indicator_crud = TechnicalIndicatorCRUD(TechnicalIndicator)
market_index_crud = MarketIndexCRUD(MarketIndex)
analysis_result_crud = AnalysisResultCRUD(AnalysisResult)
update_log_crud = DataUpdateLogCRUD(DataUpdateLog)