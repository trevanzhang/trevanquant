"""
数据库模型定义
定义所有数据库表结构
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date,
    Boolean, Text, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class Stock(Base):
    """股票基础信息表"""
    __tablename__ = "stocks"

    # 股票代码，唯一标识
    code: Mapped[str] = mapped_column(String(10), primary_key=True)

    # 股票名称
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # 所属市场：上海(SH)、深圳(SZ)、北京(BJ)
    market: Mapped[str] = mapped_column(String(5), nullable=False)

    # 行业分类
    industry: Mapped[Optional[str]] = mapped_column(String(100))

    # 上市日期
    listed_date: Mapped[Optional[date]] = mapped_column(Date)

    # 是否ST股票
    is_st: Mapped[bool] = mapped_column(Boolean, default=False)

    # 是否退市
    is_delisted: Mapped[bool] = mapped_column(Boolean, default=False)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # 索引
    __table_args__ = (
        Index('idx_stock_market', 'market'),
        Index('idx_stock_industry', 'industry'),
        Index('idx_stock_listed', 'listed_date'),
    )


class DailyData(Base):
    """日线数据表"""
    __tablename__ = "daily_data"

    # 主键ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 股票代码
    stock_code: Mapped[str] = mapped_column(String(10), nullable=False)

    # 交易日期
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)

    # 开盘价
    open_price: Mapped[float] = mapped_column(Float, nullable=False)

    # 最高价
    high_price: Mapped[float] = mapped_column(Float, nullable=False)

    # 最低价
    low_price: Mapped[float] = mapped_column(Float, nullable=False)

    # 收盘价
    close_price: Mapped[float] = mapped_column(Float, nullable=False)

    # 成交量
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    # 成交额
    amount: Mapped[Optional[float]] = mapped_column(Float)

    # 涨跌额
    change_amount: Mapped[Optional[float]] = mapped_column(Float)

    # 涨跌幅
    change_percent: Mapped[Optional[float]] = mapped_column(Float)

    # 换手率
    turnover_rate: Mapped[Optional[float]] = mapped_column(Float)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 唯一约束和索引
    __table_args__ = (
        UniqueConstraint('stock_code', 'trade_date', name='uq_stock_date'),
        Index('idx_daily_stock_date', 'stock_code', 'trade_date'),
        Index('idx_daily_trade_date', 'trade_date'),
    )


class TechnicalIndicator(Base):
    """技术指标表"""
    __tablename__ = "technical_indicators"

    # 主键ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 股票代码
    stock_code: Mapped[str] = mapped_column(String(10), nullable=False)

    # 交易日期
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)

    # 指标类型：MA, MACD, RSI, KDJ, BOLL等
    indicator_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # 指标参数，如MA5, MA10, MA20等
    indicator_param: Mapped[Optional[str]] = mapped_column(String(20))

    # 指标值
    value: Mapped[float] = mapped_column(Float, nullable=False)

    # 额外数据，JSON格式存储
    extra_data: Mapped[Optional[str]] = mapped_column(Text)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 索引
    __table_args__ = (
        Index('idx_indicator_stock_date_type', 'stock_code', 'trade_date', 'indicator_type'),
        Index('idx_indicator_type_date', 'indicator_type', 'trade_date'),
    )


class MarketIndex(Base):
    """市场指数表"""
    __tablename__ = "market_indices"

    # 主键ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 指数代码：000001(上证指数), 399001(深证成指)等
    index_code: Mapped[str] = mapped_column(String(10), nullable=False)

    # 指数名称
    index_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # 交易日期
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)

    # 开盘点数
    open_point: Mapped[float] = mapped_column(Float, nullable=False)

    # 最高点数
    high_point: Mapped[float] = mapped_column(Float, nullable=False)

    # 最低点数
    low_point: Mapped[float] = mapped_column(Float, nullable=False)

    # 收盘点数
    close_point: Mapped[float] = mapped_column(Float, nullable=False)

    # 成交量
    volume: Mapped[Optional[float]] = mapped_column(Float)

    # 成交额
    amount: Mapped[Optional[float]] = mapped_column(Float)

    # 涨跌点数
    change_point: Mapped[Optional[float]] = mapped_column(Float)

    # 涨跌幅
    change_percent: Mapped[Optional[float]] = mapped_column(Float)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 唯一约束和索引
    __table_args__ = (
        UniqueConstraint('index_code', 'trade_date', name='uq_index_date'),
        Index('idx_index_code_date', 'index_code', 'trade_date'),
        Index('idx_index_trade_date', 'trade_date'),
    )


class AnalysisResult(Base):
    """分析结果表（为策略预留）"""
    __tablename__ = "analysis_results"

    # 主键ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 股票代码
    stock_code: Mapped[str] = mapped_column(String(10), nullable=False)

    # 交易日期
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)

    # 策略名称
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # 信号类型：BUY, SELL, HOLD
    signal: Mapped[str] = mapped_column(String(10), nullable=False)

    # 信号强度 0-1
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # 目标价格
    target_price: Mapped[Optional[float]] = mapped_column(Float)

    # 止损价格
    stop_loss: Mapped[Optional[float]] = mapped_column(Float)

    # 分析原因
    reason: Mapped[Optional[str]] = mapped_column(Text)

    # 额外数据，JSON格式
    extra_data: Mapped[Optional[str]] = mapped_column(Text)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 索引
    __table_args__ = (
        Index('idx_analysis_stock_date', 'stock_code', 'trade_date'),
        Index('idx_analysis_strategy_date', 'strategy_name', 'trade_date'),
        Index('idx_analysis_signal', 'signal'),
    )


class DataUpdateLog(Base):
    """数据更新日志表"""
    __tablename__ = "data_update_logs"

    # 主键ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 数据类型：stock_info, daily_data, indicator等
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # 更新开始时间
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 更新结束时间
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 更新状态：RUNNING, SUCCESS, FAILED
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    # 处理的记录数
    records_count: Mapped[Optional[int]] = mapped_column(Integer)

    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 索引
    __table_args__ = (
        Index('idx_update_log_type_time', 'data_type', 'start_time'),
        Index('idx_update_log_status', 'status'),
    )