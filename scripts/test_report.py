#!/usr/bin/env python3
"""
报告生成测试脚本
"""

import sys
from pathlib import Path
from datetime import date

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trevanquant.report.generator import report_generator
from trevanquant.report.email_service import email_service
from trevanquant.utils.logger import setup_logger
from trevanquant.utils.config import get_config

# 设置日志
setup_logger(log_level="INFO", log_file="logs/test_report.log")


def test_report_generation():
    """测试报告生成"""
    print("=" * 50)
    print("测试报告生成")
    print("=" * 50)

    # 生成报告
    result = report_generator.generate_daily_report()

    if result['success']:
        print("✓ 报告生成成功")
        report_data = result['data']

        print(f"  标题: {report_data['title']}")
        print(f"  日期: {report_data['report_date']}")
        print(f"  生成时间: {report_data['generation_time']}")

        # 显示市场概况
        market_summary = report_data.get('market_summary', {})
        if market_summary.get('indices'):
            print(f"\n市场指数:")
            for index in market_summary['indices']:
                print(f"  {index['name']}: {index['close']:.2f} ({index['change_percent']:+.2f}%)")

        # 显示热门股票
        hot_stocks = report_data.get('hot_stocks', [])
        if hot_stocks:
            print(f"\n热门股票 (前5只):")
            for stock in hot_stocks[:5]:
                print(f"  {stock['code']} {stock['name']}: {stock['close_price']:.2f} ({stock['change_percent']:+.2f}%)")

        # 显示技术信号
        technical_signals = report_data.get('technical_signals', {})
        if technical_signals.get('buy'):
            print(f"\n买入信号: {len(technical_signals['buy'])} 只")
        if technical_signals.get('sell'):
            print(f"卖出信号: {len(technical_signals['sell'])} 只")

        # 显示数据状态
        data_status = report_data.get('data_status', [])
        if data_status:
            print(f"\n数据状态:")
            for status in data_status:
                print(f"  {status['type_name']}: {status['status_text']} ({status['records_count']} 条记录)")

    else:
        print(f"✗ 报告生成失败: {result.get('error')}")


def test_email_service():
    """测试邮件服务"""
    print("\n" + "=" * 50)
    print("测试邮件服务")
    print("=" * 50)

    config = get_config()

    # 检查邮件配置
    if not config.email.sender_email or not config.email.sender_password:
        print("✗ 邮件配置不完整")
        print("请配置以下环境变量:")
        print("  SENDER_EMAIL: 发送邮箱地址")
        print("  SENDER_PASSWORD: 发送邮箱密码/应用密码")
        print("  EMAIL_RECIPIENTS: 收件人邮箱列表(逗号分隔)")
        return

    print("✓ 邮件配置检查通过")

    # 测试连接
    print("正在测试邮件连接...")
    connection_result = email_service.test_connection()

    if connection_result['success']:
        print("✓ 邮件连接测试成功")

        # 询问是否发送测试邮件
        print("\n注意: 发送测试邮件将向配置的收件人发送邮件")
        confirm = input("是否发送测试邮件? (y/n): ")

        if confirm.lower() == 'y':
            # 生成并发送测试报告
            print("正在生成并发送测试报告...")
            result = report_generator.send_daily_report()

            if result['success'] and result['email_sent']:
                print("✓ 测试邮件发送成功")
            else:
                print(f"✗ 测试邮件发送失败: {result.get('error')}")
        else:
            print("跳过邮件发送测试")
    else:
        print(f"✗ 邮件连接测试失败: {connection_result.get('error')}")


def show_email_config_help():
    """显示邮件配置帮助"""
    print("\n" + "=" * 50)
    print("邮件配置说明")
    print("=" * 50)

    print("""
1. Gmail 配置:
   - 开启两步验证
   - 生成应用专用密码
   - 发送邮箱: your_email@gmail.com
   - SMTP服务器: smtp.gmail.com:587
   - 密码: 应用专用密码(16位)

2. 163邮箱配置:
   - 开启SMTP服务
   - 发送邮箱: your_email@163.com
   - SMTP服务器: smtp.163.com:587
   - 密码: 授权码

3. 环境变量配置:
   在项目根目录创建 .env 文件:

   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   EMAIL_RECIPIENTS=recipient1@email.com,recipient2@email.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
""")


def main():
    """主函数"""
    print("TrevanQuant 报告生成测试")
    print("=" * 50)

    try:
        # 1. 测试报告生成
        test_report_generation()

        # 2. 测试邮件服务
        test_email_service()

        # 3. 显示配置帮助
        show_email_config_help()

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