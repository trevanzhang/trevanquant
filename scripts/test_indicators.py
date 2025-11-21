#!/usr/bin/env python3
"""
技术指标测试脚本
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import date, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trevanquant.data.indicators import TechnicalIndicators
from trevanquant.database.crud import daily_data_crud
from trevanquant.database.connection import db_manager
from trevanquant.utils.logger import setup_logger

# 设置日志
setup_logger(log_level="INFO", log_file="logs/test_indicators.log")


def create_sample_daily_data():
    """创建示例日线数据"""
    print("创建示例日线数据...")

    # 生成示例数据
    dates = []
    prices = []
    base_price = 10.0

    start_date = date.today() - timedelta(days=100)
    for i in range(100):
        current_date = start_date + timedelta(days=i)
        dates.append(current_date)

        # 模拟价格波动
        change = (i % 10 - 5) * 0.1
        base_price += change
        base_price = max(1.0, base_price)  # 确保价格不为负

        prices.append(base_price)

    # 创建OHLCV数据
    data = []
    for i, (trade_date, close_price) in enumerate(zip(dates, prices)):
        data.append({
            'stock_code': '000001',
            'trade_date': trade_date,
            'open_price': close_price * 0.995,
            'high_price': close_price * 1.01,
            'low_price': close_price * 0.99,
            'close_price': close_price,
            'volume': 1000000 + i * 10000,
            'amount': close_price * 1000000
        })

    # 保存到数据库
    with db_manager.session_scope() as session:
        # 删除已存在的数据
        daily_data_crud.get_by_stock(session, '000001')
        for record in daily_data_crud.get_by_stock(session, '000001'):
            daily_data_crud.delete(session, record)

        # 批量创建新数据
        daily_data_crud.create_batch(session, data)

    print(f"✓ 创建了 {len(data)} 条示例日线数据")


def test_technical_indicators():
    """测试技术指标计算"""
    print("\n" + "=" * 50)
    print("测试技术指标计算")
    print("=" * 50)

    # 获取数据
    with db_manager.session_scope() as session:
        daily_data = daily_data_crud.get_by_stock(session, '000001')

        if not daily_data:
            print("✗ 没有找到日线数据")
            return

        # 在会话内转换为DataFrame
        df = pd.DataFrame([{
            'trade_date': d.trade_date,
            'open_price': d.open_price,
            'high_price': d.high_price,
            'low_price': d.low_price,
            'close_price': d.close_price,
            'volume': d.volume
        } for d in daily_data])

    df = df.sort_values('trade_date').reset_index(drop=True)

    print(f"使用 {len(df)} 条数据测试技术指标")

    # 测试各种指标
    indicators = {
        'MA': lambda df: TechnicalIndicators.calculate_ma(df, [5, 10, 20]),
        'EMA': lambda df: TechnicalIndicators.calculate_ema(df, [12, 26]),
        'RSI': lambda df: TechnicalIndicators.calculate_rsi(df, 14),
        'MACD': lambda df: TechnicalIndicators.calculate_macd(df),
        'KDJ': lambda df: TechnicalIndicators.calculate_kdj(df),
        'BOLL': lambda df: TechnicalIndicators.calculate_bollinger_bands(df)
    }

    results = {}

    for indicator_name, calculator in indicators.items():
        try:
            result_df = calculator(df)
            indicator_columns = [col for col in result_df.columns if col not in df.columns]
            results[indicator_name] = len(indicator_columns)
            print(f"✓ {indicator_name}: {len(indicator_columns)} 个指标")
        except Exception as e:
            print(f"✗ {indicator_name}: 计算失败 - {e}")

    print(f"\n✓ 技术指标测试完成，成功计算了 {len(results)} 类指标")


def test_indicator_calculator():
    """测试指标计算器"""
    print("\n" + "=" * 50)
    print("测试指标计算器")
    print("=" * 50)

    from trevanquant.data.indicators import indicator_calculator

    # 计算技术指标
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    result = indicator_calculator.calculate_indicators_for_stock(
        '000001',
        start_date,
        end_date,
        ['MA', 'RSI', 'MACD', 'KDJ']
    )

    if result['success']:
        print(f"✓ 指标计算器测试成功")
        print(f"  数据点数: {result['data_points']}")
        print(f"  计算指标: {result['indicators_calculated']}")
        print(f"  指标总数: {result['total_indicators']}")
    else:
        print(f"✗ 指标计算器测试失败: {result.get('error')}")


def main():
    """主函数"""
    print("TrevanQuant 技术指标测试")
    print("=" * 50)

    try:
        # 1. 创建示例数据
        create_sample_daily_data()

        # 2. 测试技术指标
        test_technical_indicators()

        # 3. 测试指标计算器
        test_indicator_calculator()

        print("\n" + "=" * 50)
        print("测试完成!")
        print("=" * 50)

        # 显示最终状态
        print("\n检查数据库中的指标数据...")
        with db_manager.session_scope() as session:
            from trevanquant.database.crud import indicator_crud
            indicators = indicator_crud.get_multi(session, limit=10)
            print(f"数据库中有 {len(indicators)} 条技术指标记录")

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()