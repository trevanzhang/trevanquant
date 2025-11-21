#!/usr/bin/env python3
"""
定时任务系统测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trevanquant.scheduler.task_scheduler import task_scheduler
from trevanquant.utils.logger import setup_logger

# 设置日志
setup_logger(log_level="INFO", log_file="logs/test_scheduler.log")


def test_scheduler_setup():
    """测试调度器设置"""
    print("=" * 50)
    print("测试调度器设置")
    print("=" * 50)

    try:
        # 设置任务（不启动调度器循环）
        task_scheduler._setup_schedules()
        print("✓ 调度器任务设置成功")

        # 显示下次运行时间
        next_runs = task_scheduler.get_next_runs()
        print(f"\n已设置 {len(next_runs)} 个定时任务:")
        for task_name, next_run in next_runs.items():
            print(f"  {task_name}: {next_run}")

    except Exception as e:
        print(f"✗ 调度器设置失败: {e}")


def test_trading_day_check():
    """测试交易日判断"""
    print("\n" + "=" * 50)
    print("测试交易日判断")
    print("=" * 50)

    try:
        is_trading = task_scheduler._is_trading_day()
        print(f"✓ 交易日判断完成，今天是{'交易日' if is_trading else '非交易日'}")
    except Exception as e:
        print(f"✗ 交易日判断失败: {e}")


def test_individual_tasks():
    """测试各个任务"""
    print("\n" + "=" * 50)
    print("测试单个任务执行")
    print("=" * 50)

    tasks = [
        ('health_check', '健康检查'),
        ('stock_list_update', '股票列表更新'),
        ('data_cleanup', '数据清理')
    ]

    for task_name, task_desc in tasks:
        print(f"\n测试任务: {task_desc}")
        try:
            result = task_scheduler.run_task_now(task_name)
            if result['success']:
                print(f"✓ {task_desc} 执行成功")
            else:
                print(f"✗ {task_desc} 执行失败: {result.get('error')}")
        except Exception as e:
            print(f"✗ {task_desc} 执行异常: {e}")


def test_report_generation():
    """测试报告生成任务"""
    print("\n" + "=" * 50)
    print("测试报告生成任务")
    print("=" * 50)

    try:
        from trevanquant.report.generator import report_generator
        from datetime import date

        result = report_generator.generate_daily_report()

        if result['success']:
            print("✓ 报告生成成功")
            report_data = result['data']
            print(f"  标题: {report_data['title']}")
            print(f"  生成时间: {report_data['generation_time']}")

            # 显示数据状态
            data_status = report_data.get('data_status', [])
            if data_status:
                print("  数据状态:")
                for status in data_status:
                    print(f"    {status['type_name']}: {status['status_text']}")
        else:
            print(f"✗ 报告生成失败: {result.get('error')}")

    except Exception as e:
        print(f"✗ 报告生成测试失败: {e}")


def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 50)
    print("系统使用说明")
    print("=" * 50)

    print("""
1. 启动持续运行模式:
   uv run python scripts/run_trevanquant.py start

2. 查看系统状态:
   uv run python scripts/run_trevanquant.py status

3. 执行单个任务:
   uv run python scripts/run_trevanquant.py run --task health_check

4. 可用任务:
   - daily_data_sync: 每日数据同步
   - daily_report: 每日报告生成
   - stock_list_update: 股票列表更新
   - technical_indicators: 技术指标计算
   - data_cleanup: 数据清理
   - health_check: 健康检查

5. 定时任务说明:
   - 工作日15:30: 数据同步
   - 工作日16:00: 报告生成
   - 每周日20:00: 股票列表更新
   - 交易时间每小时: 技术指标计算
   - 每天凌晨2点: 数据清理
   - 每30分钟: 健康检查
""")


def main():
    """主函数"""
    print("TrevanQuant 定时任务系统测试")
    print("=" * 50)

    try:
        # 1. 测试调度器设置
        test_scheduler_setup()

        # 2. 测试交易日判断
        test_trading_day_check()

        # 3. 测试各个任务
        test_individual_tasks()

        # 4. 测试报告生成
        test_report_generation()

        # 5. 显示使用说明
        show_usage()

        print("\n" + "=" * 50)
        print("测试完成!")
        print("=" * 50)

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()