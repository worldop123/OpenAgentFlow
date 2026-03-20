# OpenAgentFlow Dockerfile
# 多阶段构建

# 第一阶段：构建阶段
FROM python:3.11-slim as builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --user --no-cache-dir -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.11-slim

WORKDIR /app

# 创建非root用户
RUN groupadd -r openagentflow && useradd -r -g openagentflow openagentflow

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /home/openagentflow/.local

# 复制应用代码
COPY . .

# 设置环境变量
ENV PATH=/home/openagentflow/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 创建必要的目录
RUN mkdir -p /app/data /app/logs && \
    chown -R openagentflow:openagentflow /app

# 切换到非root用户
USER openagentflow

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)"

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]