"""
配置管理工具
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = Field(default="sqlite:///database.db")
    echo: bool = Field(default=False)


class EmailConfig(BaseModel):
    """邮件配置"""
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    sender_email: str = Field(default="")
    sender_password: str = Field(default="")
    recipients: list[str] = Field(default_factory=list)


class DataConfig(BaseModel):
    """数据获取配置"""
    request_delay: float = Field(default=1.0)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=30)
    batch_size: int = Field(default=100)


class AppConfig(BaseModel):
    """应用配置"""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    data: DataConfig = Field(default_factory=DataConfig)

    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.env_file = config_file or self.project_root / ".env"

        # 加载环境变量
        if self.env_file.exists():
            load_dotenv(self.env_file)

        # 加载配置
        self.config = self._load_config()

    def _load_config(self) -> AppConfig:
        """加载配置"""
        # 从环境变量读取配置
        config_dict = {
            "database": {
                "url": os.getenv("DATABASE_URL", "sqlite:///database.db"),
                "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true"
            },
            "email": {
                "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "sender_email": os.getenv("SENDER_EMAIL", ""),
                "sender_password": os.getenv("SENDER_PASSWORD", ""),
                "recipients": os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []
            },
            "data": {
                "request_delay": float(os.getenv("REQUEST_DELAY", "1.0")),
                "max_retries": int(os.getenv("MAX_RETRIES", "3")),
                "timeout": int(os.getenv("TIMEOUT", "30")),
                "batch_size": int(os.getenv("BATCH_SIZE", "100"))
            },
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO")
        }

        return AppConfig(**config_dict)

    def get_config(self) -> AppConfig:
        """获取配置对象"""
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        更新配置

        Args:
            updates: 配置更新字典
        """
        config_dict = self.config.model_dump()
        self._deep_update(config_dict, updates)
        self.config = AppConfig(**config_dict)

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """深度更新字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def save_to_env(self) -> None:
        """保存配置到环境变量文件"""
        env_content = []

        # 数据库配置
        env_content.append(f"DATABASE_URL={self.config.database.url}")
        env_content.append(f"DATABASE_ECHO={str(self.config.database.echo).lower()}")

        # 邮件配置
        env_content.append(f"SMTP_SERVER={self.config.email.smtp_server}")
        env_content.append(f"SMTP_PORT={self.config.email.smtp_port}")
        env_content.append(f"SENDER_EMAIL={self.config.email.sender_email}")
        env_content.append(f"SENDER_PASSWORD={self.config.email.sender_password}")
        env_content.append(f"EMAIL_RECIPIENTS={','.join(self.config.email.recipients)}")

        # 数据配置
        env_content.append(f"REQUEST_DELAY={self.config.data.request_delay}")
        env_content.append(f"MAX_RETRIES={self.config.data.max_retries}")
        env_content.append(f"TIMEOUT={self.config.data.timeout}")
        env_content.append(f"BATCH_SIZE={self.config.data.batch_size}")

        # 应用配置
        env_content.append(f"DEBUG={str(self.config.debug).lower()}")
        env_content.append(f"LOG_LEVEL={self.config.log_level}")

        # 写入文件
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_content))

    @property
    def database_url(self) -> str:
        """获取数据库URL"""
        return self.config.database.url

    @property
    def email_config(self) -> EmailConfig:
        """获取邮件配置"""
        return self.config.email

    @property
    def data_config(self) -> DataConfig:
        """获取数据配置"""
        return self.config.data


# 创建全局配置管理器实例
config_manager = ConfigManager()

# 获取配置的便捷函数
def get_config() -> AppConfig:
    """获取应用配置"""
    return config_manager.get_config()