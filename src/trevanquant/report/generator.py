"""
报告生成器
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path

from .email_service import email_service
from ..database.crud import (
    daily_data_crud, stock_crud, market_index_crud,
    indicator_crud, analysis_result_crud
)
from ..database.connection import db_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        pass

    def generate_daily_report(self, report_date: date = None) -> Dict[str, Any]:
        """
        生成每日报告

        Args:
            report_date: 报告日期，默认为今天

        Returns:
            Dict[str, Any]: 报告数据
        """
        if report_date is None:
            report_date = date.today()

        logger.info(f"开始生成 {report_date} 的每日报告")

        try:
            # 1. 获取市场概况
            market_summary = self._get_market_summary(report_date)

            # 2. 获取热门股票
            hot_stocks = self._get_hot_stocks(report_date)

            # 3. 获取技术分析信号
            technical_signals = self._get_technical_signals(report_date)

            # 4. 获取风险提示
            risk_alerts = self._get_risk_alerts(report_date)

            # 5. 获取数据更新状态
            data_status = self._get_data_status()

            # 组装报告数据
            report_data = {
                'title': f'{report_date} A股市场复盘报告',
                'report_date': report_date.strftime('%Y年%m月%d日'),
                'market_summary': market_summary,
                'hot_stocks': hot_stocks,
                'technical_signals': technical_signals,
                'risk_alerts': risk_alerts,
                'data_status': data_status,
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info(f"每日报告生成完成")
            return {'success': True, 'data': report_data}

        except Exception as e:
            logger.error(f"生成每日报告失败: {e}")
            return {'success': False, 'error': str(e)}

    def send_daily_report(
        self,
        report_date: date = None,
        recipients: List[str] = None
    ) -> Dict[str, Any]:
        """
        发送每日报告

        Args:
            report_date: 报告日期
            recipients: 收件人列表

        Returns:
            Dict[str, Any]: 发送结果
        """
        # 生成报告数据
        result = self.generate_daily_report(report_date)

        if not result['success']:
            return result

        # 发送邮件
        email_result = email_service.send_template_email(
            template_name='daily_report.html',
            subject=result['data']['title'],
            template_data=result['data'],
            recipients=recipients
        )

        return {
            'success': email_result['success'],
            'report_generated': True,
            'email_sent': email_result['success'],
            'report_data': result['data'] if result['success'] else None,
            'error': email_result.get('error')
        }

    def _get_market_summary(self, report_date: date) -> Dict[str, Any]:
        """获取市场概况"""
        try:
            with db_manager.session_scope() as session:
                # 获取主要指数
                major_indices = ['000001', '399001', '399006']  # 上证指数、深证成指、创业板指
                indices = []

                for index_code in major_indices:
                    index_data = market_index_crud.get_by_code_and_date(
                        session, index_code, report_date
                    )

                    if index_data:
                        index_name = {
                            '000001': '上证指数',
                            '399001': '深证成指',
                            '399006': '创业板指'
                        }.get(index_code, f'指数{index_code}')

                        indices.append({
                            'name': index_name,
                            'close': index_data.close_point,
                            'change': index_data.change_point or 0,
                            'change_percent': index_data.change_percent or 0,
                            'amount': index_data.amount
                        })

                # 获取市场统计数据
                daily_stats = session.query(daily_data_crud.model).filter(
                    daily_data_crud.model.trade_date == report_date
                ).all()

                up_count = len([d for d in daily_stats if d.change_percent and d.change_percent > 0])
                down_count = len([d for d in daily_stats if d.change_percent and d.change_percent < 0])
                flat_count = len([d for d in daily_stats if not d.change_percent or d.change_percent == 0])
                limit_up = len([d for d in daily_stats if d.change_percent and d.change_percent >= 9.8])
                limit_down = len([d for d in daily_stats if d.change_percent and d.change_percent <= -9.8])

                total_stocks = len(daily_stats)

                return {
                    'indices': indices,
                    'total_stocks': total_stocks,
                    'up_count': up_count,
                    'down_count': down_count,
                    'flat_count': flat_count,
                    'limit_up': limit_up,
                    'limit_down': limit_down
                }

        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return {}

    def _get_hot_stocks(self, report_date: date, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门股票（按成交额排序）"""
        try:
            with db_manager.session_scope() as session:
                # 按成交额排序获取热门股票
                hot_stocks = session.query(daily_data_crud.model).filter(
                    daily_data_crud.model.trade_date == report_date
                ).order_by(daily_data_crud.model.amount.desc()).limit(limit).all()

                result = []
                for stock_data in hot_stocks:
                    if not stock_data.amount or stock_data.amount <= 0:
                        continue

                    # 获取股票名称
                    stock_info = stock_crud.get_by_code(session, stock_data.stock_code)
                    stock_name = stock_info.name if stock_info else stock_data.stock_code

                    result.append({
                        'code': stock_data.stock_code,
                        'name': stock_name,
                        'close_price': stock_data.close_price,
                        'change_percent': stock_data.change_percent or 0,
                        'amount': stock_data.amount
                    })

                return result

        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return []

    def _get_technical_signals(self, report_date: date) -> Dict[str, List[Dict[str, Any]]]:
        """获取技术分析信号"""
        try:
            signals = {
                'buy': [],
                'sell': [],
                'hold': []
            }

            with db_manager.session_scope() as session:
                # 获取分析结果
                analysis_results = analysis_result_crud.get_buy_signals(
                    session, report_date, min_confidence=0.6
                )

                for result in analysis_results:
                    # 获取股票信息
                    stock_info = stock_crud.get_by_code(session, result.stock_code)
                    stock_name = stock_info.name if stock_info else result.stock_code

                    # 获取当前价格
                    current_data = daily_data_crud.get_by_stock_and_date(
                        session, result.stock_code, report_date
                    )
                    current_price = current_data.close_price if current_data else 0

                    signal_data = {
                        'code': result.stock_code,
                        'name': stock_name,
                        'signal_reason': result.reason or f'{result.strategy_name}策略信号',
                        'confidence': result.confidence,
                        'current_price': current_price,
                        'target_price': result.target_price,
                        'stop_loss': result.stop_loss
                    }

                    # 按信号类型分类
                    if result.signal == 'BUY':
                        signals['buy'].append(signal_data)
                    elif result.signal == 'SELL':
                        signals['sell'].append(signal_data)
                    else:
                        signals['hold'].append(signal_data)

            # 限制每个类型的数量
            for signal_type in signals:
                signals[signal_type] = signals[signal_type][:5]

            return signals

        except Exception as e:
            logger.error(f"获取技术信号失败: {e}")
            return {'buy': [], 'sell': [], 'hold': []}

    def _get_risk_alerts(self, report_date: date) -> List[Dict[str, Any]]:
        """获取风险提示"""
        alerts = []

        try:
            with db_manager.session_scope() as session:
                # 检查异常数据
                daily_stats = session.query(daily_data_crud.model).filter(
                    daily_data_crud.model.trade_date == report_date
                ).all()

                # 计算跌幅分布
                down_stocks = [d for d in daily_stats if d.change_percent and d.change_percent < -5]
                if len(down_stocks) > 100:
                    alerts.append({
                        'level': 'warning',
                        'title': '市场风险提示',
                        'message': f'今日有 {len(down_stocks)} 只股票跌幅超过5%，市场情绪较为悲观，建议注意控制风险。'
                    })

                # 检查成交额异常
                total_amount = sum([d.amount for d in daily_stats if d.amount])
                if total_amount < 5000_000_000:  # 5000亿
                    alerts.append({
                        'level': 'warning',
                        'title': '成交量提示',
                        'message': f'今日市场总成交额 {total_amount/100000000:.1f} 亿元，较平时偏低，市场活跃度下降。'
                    })

                # 检查ST股票数量
                st_stocks = session.query(stock_crud.model).filter(
                    stock_crud.model.is_st == True,
                    stock_crud.model.is_delisted == False
                ).count()

                total_stocks = session.query(stock_crud.model).filter(
                    stock_crud.model.is_delisted == False
                ).count()

                if st_stocks > 0:
                    alerts.append({
                        'level': 'info',
                        'title': 'ST股票统计',
                        'message': f'当前市场共有 {st_stocks} 只ST股票，占总数的 {st_stocks/total_stocks*100:.1f}%。'
                    })

        except Exception as e:
            logger.error(f"获取风险提示失败: {e}")

        return alerts

    def _get_data_status(self) -> List[Dict[str, Any]]:
        """获取数据更新状态"""
        try:
            from ..data.sync import data_sync_manager

            status = data_sync_manager.get_sync_status()

            if status['success']:
                type_mapping = {
                    'stock_info': '股票信息',
                    'daily_data': '日线数据',
                    'technical_indicators': '技术指标',
                    'market_indices': '市场指数'
                }

                status_mapping = {
                    'SUCCESS': '成功',
                    'FAILED': '失败',
                    'RUNNING': '运行中',
                    'NEVER': '从未更新'
                }

                result = []
                for key, value in status.items():
                    if key in type_mapping:
                        last_update = value.get('last_update', '')
                        if last_update:
                            try:
                                dt = datetime.fromisoformat(last_update)
                                last_update = dt.strftime('%Y-%m-%d %H:%M')
                            except:
                                pass

                        result.append({
                            'type_name': type_mapping[key],
                            'last_update': last_update,
                            'status': value.get('status', 'UNKNOWN'),
                            'status_text': status_mapping.get(value.get('status'), value.get('status')),
                            'records_count': value.get('records_count', 0)
                        })

                return result

        except Exception as e:
            logger.error(f"获取数据状态失败: {e}")

        return []


# 创建全局报告生成器实例
report_generator = ReportGenerator()