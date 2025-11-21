"""
主运行脚本
"""

import signal
import sys
import time
from pathlib import Path
from typing import Optional

from .task_scheduler import task_scheduler
from ..utils.logger import setup_logger, get_logger
from ..utils.config import get_config

# 设置日志
setup_logger()
logger = get_logger(__name__)


class Application:
    """应用程序主类"""

    def __init__(self):
        """初始化应用程序"""
        self.config = get_config()
        self.running = False

        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，准备退出...")
        self.running = False

    def start(self) -> None:
        """启动应用程序"""
        logger.info("启动 TrevanQuant 量化复盘系统...")

        try:
            self.running = True

            # 启动任务调度器
            task_scheduler.start()

            # 显示系统信息
            self._show_system_info()

            # 主循环
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break

        except Exception as e:
            logger.error(f"应用程序运行出错: {e}")
            raise
        finally:
            self._shutdown()

    def _show_system_info(self) -> None:
        """显示系统信息"""
        logger.info("=" * 60)
        logger.info("TrevanQuant 量化复盘系统已启动")
        logger.info("=" * 60)
        logger.info(f"运行模式: {'调试模式' if self.config.debug else '生产模式'}")
        logger.info(f"日志级别: {self.config.log_level}")

        # 显示任务调度信息
        next_runs = task_scheduler.get_next_runs()
        if next_runs:
            logger.info("定时任务:")
            for task_name, next_run in next_runs.items():
                logger.info(f"  {task_name}: {next_run}")

        logger.info("=" * 60)

    def _shutdown(self) -> None:
        """关闭应用程序"""
        logger.info("正在关闭 TrevanQuant 系统...")

        try:
            # 停止任务调度器
            task_scheduler.stop()

            logger.info("TrevanQuant 系统已安全关闭")
        except Exception as e:
            logger.error(f"关闭系统时出错: {e}")

    def run_once(self, task_name: Optional[str] = None) -> None:
        """运行单次任务"""
        logger.info("运行单次任务模式")

        if not task_name:
            logger.error("请指定要执行的任务名称")
            return

        try:
            result = task_scheduler.run_task_now(task_name)

            if result['success']:
                logger.info(f"任务执行成功: {result['message']}")
            else:
                logger.error(f"任务执行失败: {result['error']}")

        except Exception as e:
            logger.error(f"运行任务时出错: {e}")

    def show_status(self) -> None:
        """显示系统状态"""
        logger.info("TrevanQuant 系统状态")
        logger.info("=" * 40)

        try:
            # 获取数据同步状态
            from ..data.sync import data_sync_manager
            sync_status = data_sync_manager.get_sync_status()

            if sync_status['success']:
                logger.info("数据同步状态:")
                for key, value in sync_status.items():
                    if key not in ['success', 'database_stats']:
                        status = value.get('status', 'UNKNOWN')
                        records = value.get('records_count', 0)
                        logger.info(f"  {key}: {status} ({records} 条记录)")

                db_stats = sync_status.get('database_stats', {})
                if db_stats:
                    logger.info("数据库统计:")
                    for key, value in db_stats.items():
                        logger.info(f"  {key}: {value}")

            # 显示任务调度状态
            next_runs = task_scheduler.get_next_runs()
            if next_runs:
                logger.info("下次执行时间:")
                for task_name, next_run in next_runs.items():
                    logger.info(f"  {task_name}: {next_run}")

        except Exception as e:
            logger.error(f"获取状态信息失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='TrevanQuant 量化复盘系统')
    parser.add_argument(
        'command',
        choices=['start', 'run', 'status'],
        help='运行命令'
    )
    parser.add_argument(
        '--task',
        help='要执行的任务名称 (仅在run命令中使用)'
    )
    parser.add_argument(
        '--config',
        help='配置文件路径'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别'
    )

    args = parser.parse_args()

    # 更新配置
    if args.debug:
        from ..utils.config import config_manager
        config_manager.update_config({'debug': True})

    if args.log_level:
        from ..utils.config import config_manager
        config_manager.update_config({'log_level': args.log_level})
        setup_logger(log_level=args.log_level)

    # 创建应用实例
    app = Application()

    try:
        if args.command == 'start':
            # 启动持续运行模式
            app.start()

        elif args.command == 'run':
            # 运行单次任务
            app.run_once(args.task)

        elif args.command == 'status':
            # 显示系统状态
            app.show_status()

    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()