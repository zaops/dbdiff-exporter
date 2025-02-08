# 构建阶段
FROM python:3.12.5-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src ./src

# 运行阶段
FROM python:3.12.5-slim

# 安装 Oracle 和 PostgreSQL 所需的系统依赖
RUN apt-get update && apt-get install -y \
    libaio1 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -u 1000 dbdiff

# 设置工作目录
WORKDIR /app

# 从构建阶段复制安装的包和应用
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/src ./src

# 创建配置目录
RUN mkdir /config && chown dbdiff:dbdiff /config

# 切换到非 root 用户
USER dbdiff

# 设置环境变量
ENV PYTHONPATH=/app \
    CONFIG_PATH=/config/config.yaml \
    PYTHONUNBUFFERED=1

# 暴露 Prometheus 指标端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 运行应用
CMD ["python", "-m", "src.dbdiff.main"] 