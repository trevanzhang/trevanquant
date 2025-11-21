#!/usr/bin/env python3
"""
数据获取测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trevanquant.data.sync import data_sync_manager
from trevanquant.utils.logger import setup_logger

# 设置日志
setup_logger(log_level="INFO", log_file="logs/test_data_fetch.log")


def test_sync_status():
    """测试获取同步状态"""
    print("=" * 50)
    print("测试获取数据同步状态")
    print("=" * 50)

    status = data_sync_manager.get_sync_status()

    if status['success']:
        print("✓ 同步状态获取成功")
        print(f"数据库统计:")
        for key, value in status['database_stats'].items():
            print(f"  {key}: {value}")

        print(f"\n各类数据最新更新时间:")
        for key, value in status.items():
            if key not in ['success', 'database_stats']:
                last_update = value['last_update'][:19] if value['last_update'] else "从未更新"
                print(f"  {key}: {last_update} ({value['status']})")
    else:
        print(f"✗ 同步状态获取失败: {status.get('error')}")


def test_stock_list_sync():
    """测试股票列表同步"""
    print("\n" + "=" * 50)
    print("测试股票列表同步")
    print("=" * 50)

    result = data_sync_manager.sync_stock_list()

    if result['success']:
        print(f"✓ 股票列表同步成功")
        print(f"  总股票数: {result['total_stocks']}")
        print(f"  耗时: {result['duration']:.2f} 秒")
    else:
        print(f"✗ 股票列表同步失败: {result.get('error')}")


def test_daily_data_sync():
    """测试日线数据同步"""
    print("\n" + "=" * 50)
    print("测试日线数据同步（最近1天）")
    print("=" * 50)

    result = data_sync_manager.sync_daily_data(days_back=1)

    if result['success']:
        print(f"✓ 日线数据同步成功")
        print(f"  总股票数: {result['total_stocks']}")
        print(f"  成功数: {result['success_count']}")
        print(f"  失败数: {result['error_count']}")
        print(f"  总记录数: {result['total_records']}")
        print(f"  耗时: {result['duration']:.2f} 秒")
    else:
        print(f"✗ 日线数据同步失败: {result.get('error')}")


def test_technical_indicators():
    """测试技术指标计算"""
    print("\n" + "=" * 50)
    print("测试技术指标计算")
    print("=" * 50)

    from trevanquant.data.indicators import indicator_calculator
    from trevanquant.database.crud import stock_crud
    from trevanquant.database.connection import db_manager
    from datetime import date, timedelta

    # 获取一只测试股票
    with db_manager.session_scope() as session:
        stocks = stock_crud.get_active_stocks(session)
        if not stocks:
            print("✗ 没有找到股票数据")
            return

        test_stock = stocks[0]

    print(f"使用股票 {test_stock.code} - {test_stock.name} 进行测试")

    # 计算技术指标
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    result = indicator_calculator.calculate_indicators_for_stock(
        test_stock.code,
        start_date,
        end_date,
        ['MA', 'RSI', 'MACD']
    )

    if result['success']:
        print(f"✓ 技术指标计算成功")
        print(f"  数据点数: {result['data_points']}")
        print(f"  计算指标: {result['indicators_calculated']}")
        print(f"  指标总数: {result['total_indicators']}")
    else:
        print(f"✗ 技术指标计算失败: {result.get('error')}")


def main():
    """主函数"""
    print("TrevanQuant 数据获取测试")
    print("=" * 50)

    try:
        # 1. 获取同步状态
        test_sync_status()

        # 2. 测试股票列表同步
        test_stock_list_sync()

        # 3. 测试日线数据同步
        print("\n⚠️  注意: 日线数据同步会获取最近1天的所有股票数据，可能需要较长时间")
        confirm = input("是否继续测试日线数据同步? (y/n): ")
        if confirm.lower() == 'y':
            test_daily_data_sync()

        # 4. 测试技术指标计算
        test_technical_indicators()

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