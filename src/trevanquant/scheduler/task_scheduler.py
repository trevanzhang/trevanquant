"""
任务调度器
"""

import schedule
import time
import threading
from datetime import datetime, time as dt_time, timedelta
from typing import Dict, Any, Callable, Optional
from pathlib import Path

from ..data.sync import data_sync_manager
from ..report.generator import report_generator
from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        """初始化任务调度器"""
        self.config = get_config()
        self.running = False
        self.scheduler_thread = None

    def start(self) -> None:
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return

        logger.info("启动任务调度器...")
        self.running = True

        # 设置调度任务
        self._setup_schedules()

        # 在单独的线程中运行调度器
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        logger.info("任务调度器启动成功")

    def stop(self) -> None:
        """停止调度器"""
        if not self.running:
            logger.warning("调度器未在运行")
            return

        logger.info("停止任务调度器...")
        self.running = False

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        logger.info("任务调度器已停止")

    def _setup_schedules(self) -> None:
        """设置定时任务"""
        logger.info("设置定时任务...")

        # 每日数据同步任务 - 工作日15:30（收盘后）
        schedule.every().monday.at("15:30").do(self._daily_data_sync_task)
        schedule.every().tuesday.at("15:30").do(self._daily_data_sync_task)
        schedule.every().wednesday.at("15:30").do(self._daily_data_sync_task)
        schedule.every().thursday.at("15:30").do(self._daily_data_sync_task)
        schedule.every().friday.at("15:30").do(self._daily_data_sync_task)

        # 每日报告任务 - 工作日16:00
        schedule.every().monday.at("16:00").do(self._daily_report_task)
        schedule.every().tuesday.at("16:00").do(self._daily_report_task)
        schedule.every().wednesday.at("16:00").do(self._daily_report_task)
        schedule.every().thursday.at("16:00").do(self._daily_report_task)
        schedule.every().friday.at("16:00").do(self._daily_report_task)

        # 股票列表更新任务 - 每周日20:00
        schedule.every().sunday.at("20:00").do(self._stock_list_update_task)

        # 技术指标计算任务 - 每小时（交易时间）
        for hour in range(9, 16):  # 9:00 - 15:00
            schedule.every().day.at(f"{hour:02d}:00").do(self._technical_indicators_task)

        # 数据清理任务 - 每天凌晨2点
        schedule.every().day.at("02:00").do(self._data_cleanup_task)

        # 健康检查任务 - 每30分钟
        schedule.every(30).minutes.do(self._health_check_task)

        logger.info("定时任务设置完成")

    def _run_scheduler(self) -> None:
        """运行调度器循环"""
        logger.info("调度器开始运行...")

        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"调度器运行出错: {e}")
                time.sleep(5)  # 出错后等待5秒再继续

        logger.info("调度器运行结束")

    def _daily_data_sync_task(self) -> None:
        """每日数据同步任务"""
        logger.info("开始执行每日数据同步任务")

        if not self._is_trading_day():
            logger.info("今天不是交易日，跳过数据同步")
            return

        try:
            # 执行完整数据同步
            result = data_sync_manager.full_sync()

            if result['success']:
                logger.info(f"数据同步任务完成: {result}")
            else:
                logger.error(f"数据同步任务失败: {result}")

        except Exception as e:
            logger.error(f"数据同步任务异常: {e}")

    def _daily_report_task(self) -> None:
        """每日报告任务"""
        logger.info("开始执行每日报告任务")

        if not self._is_trading_day():
            logger.info("今天不是交易日，跳过报告生成")
            return

        try:
            # 生成并发送报告
            result = report_generator.send_daily_report()

            if result['success']:
                logger.info(f"每日报告任务完成: 邮件发送={result['email_sent']}")
            else:
                logger.error(f"每日报告任务失败: {result}")

        except Exception as e:
            logger.error(f"每日报告任务异常: {e}")

    def _stock_list_update_task(self) -> None:
        """股票列表更新任务"""
        logger.info("开始执行股票列表更新任务")

        try:
            result = data_sync_manager.sync_stock_list()

            if result['success']:
                logger.info(f"股票列表更新完成: {result['total_stocks']} 只股票")
            else:
                logger.error(f"股票列表更新失败: {result}")

        except Exception as e:
            logger.error(f"股票列表更新任务异常: {e}")

    def _technical_indicators_task(self) -> None:
        """技术指标计算任务"""
        logger.info("开始执行技术指标计算任务")

        if not self._is_trading_day():
            logger.info("今天不是交易日，跳过技术指标计算")
            return

        try:
            # 计算最近5天的技术指标
            result = data_sync_manager.sync_technical_indicators(days_back=5)

            if result['success']:
                logger.info(f"技术指标计算完成: {result}")
            else:
                logger.error(f"技术指标计算失败: {result}")

        except Exception as e:
            logger.error(f"技术指标计算任务异常: {e}")

    def _data_cleanup_task(self) -> None:
        """数据清理任务"""
        logger.info("开始执行数据清理任务")

        try:
            # 清理30天前的日志文件
            self._cleanup_logs(days_to_keep=30)

            # 可以添加其他清理任务
            logger.info("数据清理任务完成")

        except Exception as e:
            logger.error(f"数据清理任务异常: {e}")

    def _health_check_task(self) -> None:
        """健康检查任务"""
        try:
            # 检查数据库连接
            from ..database.connection import db_manager

            with db_manager.session_scope() as session:
                # 简单查询测试连接
                session.execute("SELECT 1")

            # 检查配置文件
            config = get_config()
            if not config.email.sender_email:
                logger.warning("邮件配置不完整")

            # 检查磁盘空间
            logs_dir = Path("logs")
            if logs_dir.exists():
                total_size = sum(f.stat().st_size for f in logs_dir.rglob('*') if f.is_file())
                if total_size > 100 * 1024 * 1024:  # 100MB
                    logger.warning(f"日志文件过大: {total_size / 1024 / 1024:.1f}MB")

        except Exception as e:
            logger.error(f"健康检查失败: {e}")

    def _is_trading_day(self) -> bool:
        """判断今天是否为交易日"""
        try:
            today = datetime.now().date()

            # 检查是否为周末
            if today.weekday() >= 5:  # 周六、周日
                return False

            # 这里可以添加更复杂的交易日判断逻辑
            # 比如查询节假日数据等

            return True

        except Exception as e:
            logger.error(f"判断交易日失败: {e}")
            return False  # 出错时默认不执行

    def _cleanup_logs(self, days_to_keep: int = 30) -> None:
        """清理日志文件"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    logger.info(f"删除过期日志文件: {log_file}")

        except Exception as e:
            logger.error(f"清理日志文件失败: {e}")

    def get_next_runs(self) -> Dict[str, str]:
        """获取下次运行时间"""
        try:
            jobs = schedule.get_jobs()
            next_runs = {}

            for job in jobs:
                if hasattr(job, 'next_run') and job.next_run:
                    job_name = str(job.job_func)
                    # 提取函数名
                    if hasattr(job.job_func, '__name__'):
                        job_name = job.job_func.__name__

                    next_runs[job_name] = job.next_run.strftime('%Y-%m-%d %H:%M:%S')

            return next_runs

        except Exception as e:
            logger.error(f"获取下次运行时间失败: {e}")
            return {}

    def run_task_now(self, task_name: str) -> Dict[str, Any]:
        """立即执行指定任务"""
        logger.info(f"立即执行任务: {task_name}")

        try:
            task_map = {
                'daily_data_sync': self._daily_data_sync_task,
                'daily_report': self._daily_report_task,
                'stock_list_update': self._stock_list_update_task,
                'technical_indicators': self._technical_indicators_task,
                'data_cleanup': self._data_cleanup_task,
                'health_check': self._health_check_task,
            }

            if task_name not in task_map:
                return {'success': False, 'error': f'未知任务: {task_name}'}

            # 执行任务
            task_map[task_name]()

            return {'success': True, 'message': f'任务 {task_name} 执行完成'}

        except Exception as e:
            logger.error(f"执行任务 {task_name} 失败: {e}")
            return {'success': False, 'error': str(e)}


# 创建全局任务调度器实例
task_scheduler = TaskScheduler()