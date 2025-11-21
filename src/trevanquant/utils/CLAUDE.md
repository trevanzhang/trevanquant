[根目录](../../../CLAUDE.md) > [src/trevanquant](../../) > **utils**

# Utils 模块

## 模块职责

Utils模块提供系统的基础工具和服务，包括日志管理、配置管理和通用工具函数。这些工具被其他模块广泛使用，是系统稳定运行的基础设施。

## 入口与启动

### 主要入口文件
- **logger.py**: 日志管理工具，提供统一的日志记录接口
- **config.py**: 配置管理工具，处理系统配置和环境变量

### 核心实例
```python
from trevanquant.utils.logger import get_logger, setup_logger
from trevanquant.utils.config import get_config, config_manager

# 全局配置和日志实例
logger = get_logger(__name__)
config = get_config()
```

## 对外接口

### 日志管理接口
```python
def setup_logger(log_level: str = "INFO", log_file: str = None) -> None
def get_logger(name: str) -> Logger
```

### 配置管理接口
```python
class ConfigManager:
    def get_config(self) -> AppConfig
    def update_config(self, updates: Dict[str, Any]) -> None
    def save_to_env(self) -> None
    def database_url(self) -> str
    def email_config(self) -> EmailConfig
    def data_config(self) -> DataConfig
```

## 日志管理

### 日志配置
```python
LOG_LEVEL = "INFO"        # 日志级别
LOG_FILE = "logs/app.log" # 日志文件路径
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 日志级别
- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息记录
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志特性
- 自动创建日志目录
- 日志文件轮转（按大小）
- 控制台和文件双输出
- 结构化日志格式
- 异常堆栈跟踪

### 日志使用示例
```python
from trevanquant.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("系统启动")
logger.warning("配置文件缺失")
logger.error("数据库连接失败", exc_info=True)
```

## 配置管理

### 配置模型
使用Pydantic进行配置验证和类型安全：

```python
class DatabaseConfig(BaseModel):
    url: str = Field(default="sqlite:///database.db")
    echo: bool = Field(default=False)

class EmailConfig(BaseModel):
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    sender_email: str = Field(default="")
    sender_password: str = Field(default="")
    recipients: list[str] = Field(default_factory=list)

class DataConfig(BaseModel):
    request_delay: float = Field(default=1.0)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=30)
    batch_size: int = Field(default=100)
```

### 环境变量配置
```bash
# 数据库配置
DATABASE_URL=sqlite:///database.db
DATABASE_ECHO=false

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@email.com,recipient2@email.com

# 应用配置
DEBUG=false
LOG_LEVEL=INFO

# 数据获取配置
REQUEST_DELAY=1.0
MAX_RETRIES=3
TIMEOUT=30
BATCH_SIZE=100
```

### 配置加载顺序
1. 默认值（在模型中定义）
2. 环境变量文件(.env)
3. 系统环境变量
4. 运行时更新

## 关键依赖与配置

### 外部依赖
- **python-dotenv>=1.0.0**: 环境变量加载
- **pydantic>=2.4.0**: 数据验证和设置管理
- **loguru>=0.7.0**: 高级日志库

### 配置文件结构
```
project_root/
├── .env                    # 环境变量配置
├── .env.example           # 配置模板（待创建）
└── logs/
    ├── app.log            # 应用主日志
    └── error.log          # 错误日志
```

## 配置验证

### 自动验证
- 数据类型检查
- 格式验证（邮箱、URL等）
- 范围验证（端口号、超时时间等）
- 必填字段检查

### 错误处理
- 配置文件不存在时使用默认值
- 格式错误时给出明确提示
- 运行时配置更新验证

## 性能优化

### 日志性能
- 异步日志写入
- 日志缓冲机制
- 按需日志级别过滤

### 配置缓存
- 配置对象缓存
- 延迟加载机制
- 内存占用优化

## 测试与质量

### 质量保证
- 配置模型类型安全
- 日志记录完整性
- 错误处理覆盖
- 向后兼容性

### 测试覆盖
- 配置加载测试
- 日志功能测试
- 环境变量解析测试

## 常见问题 (FAQ)

### Q: 如何修改日志级别？
A: 在.env文件中设置LOG_LEVEL=DEBUG，或在代码中调用setup_logger(log_level="DEBUG")。

### Q: 配置文件在哪里？
A: 默认在项目根目录的.env文件中，如果没有会自动创建。

### Q: 如何添加新的配置项？
A: 在相应的Config类中添加字段定义，并在.env文件中设置对应的环境变量。

### Q: 日志文件太大怎么办？
A: 日志系统会自动管理文件大小，或手动删除logs目录下的旧日志文件。

### Q: 配置更新后如何生效？
A: 重启应用程序，或使用config_manager.update_config()运行时更新。

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `logger.py` - 日志管理
- `config.py` - 配置管理

### 配置文件
- `../../../.env` - 环境变量配置
- `../../../.env.example` - 配置模板（待创建）

### 日志目录
- `../../../logs/` - 日志文件目录

## 扩展计划

### 计划功能
- 加密配置支持
- 远程配置中心集成
- 日志聚合和分析
- 配置热重载机制

## 变更记录 (Changelog)

### 2025-11-21 - 模块文档创建
- 创建utils模块CLAUDE.md文档
- 详细说明日志和配置管理功能
- 添加配置示例和故障排除指南

---

*本文档由AI辅助生成，最后更新时间：2025-11-21*