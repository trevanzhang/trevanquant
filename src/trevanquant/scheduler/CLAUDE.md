[根目录](../../../CLAUDE.md) > [src/trevanquant](../../) > **scheduler**

# Scheduler 模块

## 模块职责

Scheduler模块是系统的任务调度核心，负责管理和执行所有定时任务，包括数据同步、报告生成、系统维护等自动化操作。支持手动触发和状态监控功能。

## 入口与启动

### 主要入口文件
- **task_scheduler.py**: 任务调度器，管理所有定时任务
- **runner.py**: 主运行器，提供系统启动和管理接口

### 系统启动
```bash
# 启动系统（持续运行模式）
python scripts/run_trevanquant.py start

# 执行单次任务
python scripts/run_trevanquant.py run --task daily_report

# 查看系统状态
python scripts/run_trevanquant.py status
```

## 对外接口

### TaskScheduler类
```python
class TaskScheduler:
    def start(self) -> None
    def stop(self) -> None
    def get_next_runs(self) -> Dict[str, str]
    def run_task_now(self, task_name: str) -> Dict[str, Any]
```

### Application类
```python
class Application:
    def start(self) -> None
    def run_once(self, task_name: Optional[str] = None) -> None
    def show_status(self) -> None
    def _shutdown(self) -> None
```

## 定时任务安排

### 每日任务
| 任务名称 | 执行时间 | 说明 | 触发条件 |
|---------|---------|------|---------|
| 数据同步 | 工作日15:30 | 获取当日股票数据 | 交易日判断 |
| 报告生成 | 工作日16:00 | 生成并发送邮件报告 | 交易日判断 |

### 每周任务
| 任务名称 | 执行时间 | 说明 |
|---------|---------|------|
| 股票列表更新 | 每周日20:00 | 更新A股股票列表 |

### 每日例行任务
| 任务名称 | 执行时间 | 说明 |
|---------|---------|------|
| 技术指标计算 | 交易时间每小时(9:00-15:00) | 计算技术指标 |
| 数据清理 | 每天凌晨2:00 | 清理过期日志 |
| 健康检查 | 每30分钟 | 系统健康检查 |

## 任务管理

### 任务执行流程
1. 调度器检查任务时间
2. 判断交易日条件
3. 执行任务逻辑
4. 记录执行结果
5. 异常处理和重试

### 交易日判断
```python
def _is_trading_day(self) -> bool:
    """判断今天是否为交易日"""
    today = datetime.now().date()
    # 检查周末
    if today.weekday() >= 5:  # 周六、周日
        return False
    # 可扩展节假日检查
    return True
```

### 任务类型
- **daily_data_sync**: 每日数据同步
- **daily_report**: 每日报告生成
- **stock_list_update**: 股票列表更新
- **technical_indicators**: 技术指标计算
- **data_cleanup**: 数据清理
- **health_check**: 健康检查

## 系统监控

### 健康检查内容
- 数据库连接测试
- 配置文件完整性
- 磁盘空间检查
- 日志文件大小监控

### 状态信息
- 下次任务执行时间
- 数据同步状态
- 数据库统计信息
- 系统运行状态

## 信号处理

### 支持的信号
- **SIGINT**: Ctrl+C中断信号
- **SIGTERM**: 终止信号

### 优雅关闭流程
1. 接收到关闭信号
2. 停止调度器
3. 等待当前任务完成
4. 清理资源
5. 安全退出

## 关键依赖与配置

### 外部依赖
- **schedule>=1.2.0**: 任务调度库
- **threading**: 多线程支持

### 配置参数
```python
DEBUG = false           # 调试模式
LOG_LEVEL = "INFO"      # 日志级别
```

## 性能优化

### 多线程设计
- 调度器在独立线程中运行
- 主线程负责信号处理
- 避免阻塞主程序

### 错误恢复
- 任务执行异常时记录日志
- 调度器出错后自动重启
- 不影响其他任务执行

## 测试与质量

### 测试文件
- `../../../scripts/test_scheduler.py` - 调度器测试

### 质量保证
- 完整的错误处理
- 日志记录和监控
- 信号安全处理
- 资源清理机制

## 常见问题 (FAQ)

### Q: 任务没有按时执行？
A: 检查系统时间设置，确认交易日判断逻辑是否正确。

### Q: 如何修改任务执行时间？
A: 在task_scheduler.py中的_setup_schedules方法中修改时间设置。

### Q: 系统无法正常关闭？
A: 检查是否有长时间运行的任务，使用SIGINT信号优雅关闭。

### Q: 如何添加新的定时任务？
A: 在_setup_schedules方法中添加新的schedule.every()配置。

### Q: 调度器停止后如何重启？
A: 重新运行启动脚本，或使用systemd等进程管理工具。

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `task_scheduler.py` - 任务调度器
- `runner.py` - 主运行器

### 启动脚本
- `../../../scripts/run_trevanquant.py` - 主启动脚本

### 测试文件
- `../../../scripts/test_scheduler.py` - 调度器测试

### 日志目录
- `../../../logs/` - 系统日志文件

## 变更记录 (Changelog)

### 2025-11-21 - 模块文档创建
- 创建scheduler模块CLAUDE.md文档
- 详细说明任务调度和系统管理功能
- 添加定时任务配置和监控指南

---

*本文档由AI辅助生成，最后更新时间：2025-11-21*