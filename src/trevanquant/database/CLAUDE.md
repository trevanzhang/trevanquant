[根目录](../../../CLAUDE.md) > [src/trevanquant](../../) > **database**

# Database 模块

## 模块职责

Database模块负责系统中所有数据持久化相关功能，包括数据模型定义、数据库连接管理、CRUD操作和数据库迁移。

## 入口与启动

### 主要入口文件
- **models.py**: 定义所有数据库表结构和模型类
- **connection.py**: 数据库连接管理和会话控制
- **crud.py**: 数据库操作接口封装
- **migrations.py**: 数据库迁移和初始化脚本

### 初始化流程
```python
# 数据库初始化
from trevanquant.database.connection import db_manager
from trevanquant.database.migrations import init_database

# 自动创建表结构
db_manager.create_tables()

# 执行迁移初始化
init_database()
```

## 对外接口

### DatabaseManager类
```python
class DatabaseManager:
    def __init__(self, database_url: str = None)
    def create_tables(self) -> None
    def drop_tables(self) -> None
    def get_session(self) -> Session
    def session_scope(self) -> Generator[Session, None, None]
    def execute_sql(self, sql: str) -> None
```

### CRUD操作接口
- **stock_crud**: 股票信息数据操作
- **daily_data_crud**: 日线数据操作
- **indicator_crud**: 技术指标数据操作
- **market_index_crud**: 市场指数数据操作
- **update_log_crud**: 更新日志操作
- **analysis_result_crud**: 分析结果操作

## 关键依赖与配置

### 依赖项
- SQLAlchemy 2.0+ (ORM框架)
- SQLite (默认数据库)

### 配置参数
```python
DATABASE_URL = "sqlite:///database.db"  # 数据库连接URL
DATABASE_ECHO = false                  # 是否显示SQL语句
```

### 数据库表结构
1. **stocks** - 股票基础信息
2. **daily_data** - 日线交易数据
3. **technical_indicators** - 技术指标数据
4. **market_indices** - 市场指数数据
5. **analysis_results** - 分析结果(预留)
6. **data_update_logs** - 数据更新日志

## 数据模型

### 核心模型类
- **Stock**: 股票基础信息模型
- **DailyData**: 日线数据模型
- **TechnicalIndicator**: 技术指标模型
- **MarketIndex**: 市场指数模型
- **AnalysisResult**: 分析结果模型
- **DataUpdateLog**: 更新日志模型

### 模型特性
- 使用SQLAlchemy 2.0现代ORM语法
- 支持类型注解和Pydantic验证
- 包含完整的索引和约束定义
- 自动时间戳管理

## 测试与质量

### 测试覆盖
- 数据库连接测试
- CRUD操作测试
- 模型关系验证
- 迁移脚本测试

### 质量保证
- 使用上下文管理器确保会话安全
- 支持事务回滚机制
- 完整的错误处理
- 类型安全检查

## 常见问题 (FAQ)

### Q: 如何切换到其他数据库？
A: 修改DATABASE_URL环境变量，支持MySQL、PostgreSQL等。

### Q: 数据库文件在哪里？
A: 默认在项目根目录的database.db文件中。

### Q: 如何执行数据库迁移？
A: 运行`python src/trevanquant/database/migrations.py init`初始化数据库。

### Q: 如何备份数据？
A: 直接复制database.db文件，或使用SQLite的备份命令。

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `models.py` - 数据模型定义
- `connection.py` - 连接管理
- `crud.py` - CRUD操作
- `migrations.py` - 迁移脚本

### 配置文件
- `../../../.env` - 环境配置
- `../../../database.db` - SQLite数据库文件

### 测试文件
- `../../../tests/test_database.py` - 数据库测试

## 变更记录 (Changelog)

### 2025-11-21 - 模块文档创建
- 创建database模块CLAUDE.md文档
- 完善模块接口和功能说明
- 添加常见问题和故障排除指南

---

*本文档由AI辅助生成，最后更新时间：2025-11-21*