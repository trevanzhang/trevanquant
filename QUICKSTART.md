# 快速开始指南

本指南将帮助您在5分钟内快速部署和运行 TrevanQuant 量化复盘系统。

## 🚀 快速部署（推荐）

### 前置要求
- Docker 和 Docker Compose
- Git

### 1. 克隆并配置

```bash
# 克隆项目
git clone https://github.com/your-username/trevanquant.git
cd trevanquant

# 复制环境配置
cp .env.example .env
```

### 2. 配置邮件（重要！）

编辑 `.env` 文件：

```bash
nano .env
```

**必需配置项：**
```env
# Gmail配置示例
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16_digit_app_password
EMAIL_RECIPIENTS=recipient@email.com
```

> ⚠️ **重要**: Gmail需要使用应用专用密码，不是登录密码！

### 3. 一键部署

```bash
# 给脚本执行权限
chmod +x scripts/deploy.sh

# 一键部署
./scripts/deploy.sh
```

### 4. 验证部署

```bash
# 查看运行状态
./scripts/deploy.sh status

# 查看日志
./scripts/deploy.sh logs
```

## 🛠️ 本地开发部署

### 前置要求
- Python 3.11+
- uv (推荐) 或 pip

### 1. 安装依赖

```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/your-username/trevanquant.git
cd trevanquant

# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate
```

### 2. 配置邮件

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置（同上）
nano .env
```

### 3. 初始化数据库

```bash
# 创建数据库表
uv run python src/trevanquant/database/migrations.py init

# 创建示例数据
uv run python src/trevanquant/database/migrations.py sample
```

### 4. 运行测试

```bash
# 测试报告生成
uv run python scripts/test_report.py

# 如果邮件配置正确，可以测试发送报告
```

### 5. 启动系统

```bash
# 启动定时任务调度器
uv run python scripts/run_trevanquant.py start

# 或查看状态
uv run python scripts/run_trevanquant.py status
```

## 📧 邮件配置详细说明

### Gmail 配置步骤

1. **开启两步验证**
   - 访问 [Google账户设置](https://myaccount.google.com/)
   - 安全 → 两步验证 → 开启

2. **生成应用专用密码**
   - 安全 → 应用专用密码
   - 选择应用：邮件
   - 选择设备：其他（自定义名称）
   - 生成16位密码

3. **配置环境变量**
   ```env
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=xxxx-xxxx-xxxx-xxxx  # 16位密码
   EMAIL_RECIPIENTS=recipient@email.com
   ```

### 163邮箱配置步骤

1. **开启SMTP服务**
   - 登录163邮箱 → 设置 → POP3/SMTP/IMAP
   - 开启SMTP服务

2. **获取授权码**
   - 按提示发送短信获取授权码

3. **配置环境变量**
   ```env
   SENDER_EMAIL=your_email@163.com
   SENDER_PASSWORD=your_auth_code
   SMTP_SERVER=smtp.163.com
   SMTP_PORT=587
   EMAIL_RECIPIENTS=recipient@email.com
   ```

## 🎯 系统验证

### 检查系统状态

```bash
# Docker部署
./scripts/deploy.sh status

# 本地部署
uv run python scripts/run_trevanquant.py status
```

### 手动测试

```bash
# 测试报告生成（不发送邮件）
uv run python scripts/test_report.py

# 测试技术指标计算
uv run python scripts/test_indicators.py

# 测试调度器
uv run python scripts/test_scheduler.py
```

### 查看日志

```bash
# Docker部署日志
./scripts/deploy.sh logs

# 本地日志
tail -f logs/app.log
```

## ⏰ 定时任务验证

系统预设以下自动任务：

- **工作日15:30**: 自动获取当日股票数据
- **工作日16:00**: 自动生成并发送邮件报告
- **每30分钟**: 系统健康检查

验证方式：
1. 等待下一个定时任务执行时间
2. 查看日志确认任务执行
3. 检查邮箱是否收到报告

## 🆘 常见问题

### Q: 邮件发送失败怎么办？

A: 检查以下几点：
1. 邮箱配置是否正确（特别是密码）
2. 是否使用了应用专用密码（Gmail）
3. 网络连接是否正常
4. 收件人邮箱格式是否正确

### Q: 如何修改定时任务时间？

A: 编辑 `src/trevanquant/scheduler/task_scheduler.py` 中的 `_setup_schedules` 方法。

### Q: 如何添加更多技术指标？

A: 在 `src/trevanquant/data/indicators.py` 中添加新的计算函数。

### Q: 数据获取失败怎么办？

A: 检查网络连接，必要时调整 `REQUEST_DELAY` 参数。

### Q: 如何备份数据？

A: 备份 `database.db` 文件即可。

## 📞 获取帮助

- 📖 查看 [完整文档](README.md)
- 🐛 提交 [Issue](https://github.com/your-username/trevanquant/issues)
- 💬 参与 [讨论](https://github.com/your-username/trevanquant/discussions)

---

🎉 **恭喜！** 您已成功部署 TrevanQuant 量化复盘系统！