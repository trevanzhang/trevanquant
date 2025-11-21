# 使用Python 3.11官方镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# 创建必要的目录
RUN mkdir -p logs data config

# 安装项目依赖
RUN uv sync --frozen

# 创建非root用户
RUN groupadd -r trevanquant && useradd -r -g trevanquant trevanquant
RUN chown -R trevanquant:trevanquant /app
USER trevanquant

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "from trevanquant.database.connection import db_manager; db_manager.get_session().close()" || exit 1

# 暴露端口（如果需要Web界面）
EXPOSE 8000

# 默认命令
CMD ["uv", "run", "python", "scripts/run_trevanquant.py", "start"]