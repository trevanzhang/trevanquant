"""
数据库迁移和初始化脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from trevanquant.database.connection import db_manager
from trevanquant.database.crud import stock_crud, update_log_crud


def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")

    # 创建所有表
    db_manager.create_tables()
    print("✓ 数据库表创建完成")

    # 创建基础数据（可选）
    init_base_data()
    print("✓ 基础数据初始化完成")


def init_base_data():
    """初始化基础数据"""
    with db_manager.session_scope() as session:
        # 创建数据更新日志类型
        log_types = ['stock_info', 'daily_data', 'technical_indicators', 'market_indices']

        for log_type in log_types:
            existing_log = update_log_crud.get_latest_by_type(session, log_type)
            if not existing_log:
                update_log_crud.create_log(session, log_type, "SUCCESS")
                print(f"  - 创建日志类型: {log_type}")


def reset_database():
    """重置数据库（谨慎使用）"""
    confirm = input("⚠️  这将删除所有数据，确认继续吗？ (yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return

    print("正在重置数据库...")

    # 删除所有表
    db_manager.drop_tables()
    print("✓ 数据库表删除完成")

    # 重新创建表
    init_database()
    print("✓ 数据库重置完成")


def check_database():
    """检查数据库状态"""
    print("正在检查数据库状态...")

    with db_manager.session_scope() as session:
        # 检查表是否存在并获取记录数
        from trevanquant.database.models import Stock, DailyData, TechnicalIndicator

        tables = [
            ("股票信息", Stock),
            ("日线数据", DailyData),
            ("技术指标", TechnicalIndicator),
        ]

        for table_name, model in tables:
            count = session.query(model).count()
            print(f"  {table_name}: {count} 条记录")


def create_sample_stock():
    """创建示例股票数据（用于测试）"""
    print("正在创建示例股票数据...")

    sample_stocks = [
        {
            'code': '000001',
            'name': '平安银行',
            'market': 'SZ',
            'industry': '银行',
            'is_st': False,
            'is_delisted': False
        },
        {
            'code': '000002',
            'name': '万科A',
            'market': 'SZ',
            'industry': '房地产',
            'is_st': False,
            'is_delisted': False
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'market': 'SH',
            'industry': '银行',
            'is_st': False,
            'is_delisted': False
        },
        {
            'code': '600036',
            'name': '招商银行',
            'market': 'SH',
            'industry': '银行',
            'is_st': False,
            'is_delisted': False
        }
    ]

    with db_manager.session_scope() as session:
        for stock_data in sample_stocks:
            existing = stock_crud.get_by_code(session, stock_data['code'])
            if existing:
                print(f"  - 股票 {stock_data['code']} 已存在，跳过")
                continue

            stock_crud.create(session, stock_data)
            print(f"  + 创建股票: {stock_data['code']} - {stock_data['name']}")

    print("✓ 示例股票数据创建完成")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python migrations.py init      - 初始化数据库")
        print("  python migrations.py reset     - 重置数据库")
        print("  python migrations.py check     - 检查数据库状态")
        print("  python migrations.py sample    - 创建示例数据")
        return

    command = sys.argv[1]

    if command == 'init':
        init_database()
    elif command == 'reset':
        reset_database()
    elif command == 'check':
        check_database()
    elif command == 'sample':
        create_sample_stock()
    else:
        print(f"未知命令: {command}")


if __name__ == '__main__':
    main()