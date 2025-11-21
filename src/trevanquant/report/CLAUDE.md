[根目录](../../../CLAUDE.md) > [src/trevanquant](../../) > **report**

# Report 模块

## 模块职责

Report模块负责生成和发送分析报告，包括市场概况、热门股票分析、技术信号和风险提示。系统通过邮件自动发送每日复盘报告，帮助用户及时了解市场动态。

## 入口与启动

### 主要入口文件
- **generator.py**: 报告生成器，负责收集和分析数据
- **email_service.py**: 邮件发送服务，支持模板邮件和附件

### 核心实例
```python
from trevanquant.report.generator import report_generator
from trevanquant.report.email_service import email_service

# 全局报告服务实例
report_generator = ReportGenerator()
email_service = EmailService()
```

## 对外接口

### ReportGenerator类
```python
class ReportGenerator:
    def generate_daily_report(self, report_date: date = None) -> Dict[str, Any]
    def send_daily_report(self, report_date: date = None, recipients: List[str] = None) -> Dict[str, Any]
    def _get_market_summary(self, report_date: date) -> Dict[str, Any]
    def _get_hot_stocks(self, report_date: date, limit: int = 10) -> List[Dict[str, Any]]
    def _get_technical_signals(self, report_date: date) -> Dict[str, List[Dict[str, Any]]]
    def _get_risk_alerts(self, report_date: date) -> List[Dict[str, Any]]
    def _get_data_status(self) -> List[Dict[str, Any]]
```

### EmailService类
```python
class EmailService:
    def send_email(self, subject: str, content: str, recipients: List[str] = None,
                   attachments: List[str] = None, html_content: bool = True) -> Dict[str, Any]
    def send_template_email(self, template_name: str, subject: str, template_data: Dict[str, Any],
                           recipients: List[str] = None, attachments: List[str] = None) -> Dict[str, Any]
    def test_connection(self) -> Dict[str, Any]
```

## 关键依赖与配置

### 外部依赖
- **jinja2>=3.1.0**: 模板引擎
- **yagmail>=0.15.0**: 邮件发送库

### 邮件配置
```python
SMTP_SERVER = "smtp.gmail.com"    # SMTP服务器
SMTP_PORT = 587                   # SMTP端口
SENDER_EMAIL = ""                 # 发件人邮箱
SENDER_PASSWORD = ""              # 邮件密码/应用专用密码
EMAIL_RECIPIENTS = []             # 收件人列表
```

### 模板目录
- `templates/daily_report.html` - 每日报告邮件模板
- `templates/` - 其他邮件模板目录

## 报告内容结构

### 市场概况
- 主要指数表现（上证指数、深证成指、创业板指）
- 市场统计数据（涨跌股票数量、涨停跌停数量）
- 成交额和活跃度分析

### 热门股票
- 按成交额排序的热门股票
- 包含股票代码、名称、价格和涨跌幅
- 限制显示前10只

### 技术信号
- 买入信号：基于技术分析的买入建议
- 卖出信号：基于技术分析的卖出建议
- 持有建议：中性持仓建议
- 每个信号包含置信度和原因

### 风险提示
- 市场异常波动提醒
- 成交量异常提示
- ST股票统计信息
- 其他风险因素

### 数据状态
- 各类数据更新状态
- 数据完整性检查
- 系统健康状态

## 邮件模板系统

### 模板特性
- 支持Jinja2模板语法
- 动态数据绑定
- HTML格式支持
- 响应式设计

### 模板数据结构
```python
template_data = {
    'title': '报告标题',
    'report_date': '报告日期',
    'market_summary': '市场概况',
    'hot_stocks': '热门股票',
    'technical_signals': '技术信号',
    'risk_alerts': '风险提示',
    'data_status': '数据状态',
    'generation_time': '生成时间'
}
```

## 定时报告

### 发送时间
- 工作日16:00自动发送
- 仅在交易日执行
- 支持手动触发发送

### 报告生成流程
1. 检查是否为交易日
2. 收集当日市场数据
3. 计算技术指标和信号
4. 分析市场风险
5. 生成HTML报告
6. 发送邮件给订阅者

## 测试与质量

### 测试文件
- `../../../scripts/test_report.py` - 报告功能测试

### 质量保证
- 邮件发送前连接测试
- 模板渲染验证
- 数据完整性检查
- 错误处理和重试机制

## 常见问题 (FAQ)

### Q: 邮件发送失败怎么办？
A: 检查邮件配置，确认SMTP服务器设置和认证信息正确。

### Q: 如何自定义邮件模板？
A: 在templates目录下创建新的HTML模板，使用Jinja2语法。

### Q: 报告数据不准确？
A: 确保数据同步正常，检查数据库中的最新数据。

### Q: 如何添加新的收件人？
A: 在.env文件中的EMAIL_RECIPIENTS参数中添加邮箱地址。

### Q: Gmail发送失败？
A: 需要开启两步验证并使用应用专用密码，不能使用普通密码。

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `generator.py` - 报告生成器
- `email_service.py` - 邮件服务

### 模板文件
- `templates/daily_report.html` - 每日报告模板（待创建）
- `templates/` - 其他邮件模板目录

### 测试文件
- `../../../scripts/test_report.py` - 报告测试脚本

### 配置文件
- `../../../.env` - 邮件配置

## 变更记录 (Changelog)

### 2025-11-21 - 模块文档创建
- 创建report模块CLAUDE.md文档
- 详细说明报告生成和邮件发送功能
- 添加配置指南和故障排除说明

---

*本文档由AI辅助生成，最后更新时间：2025-11-21*