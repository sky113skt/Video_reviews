FROM python:3.10-slim
# 使用阿里云 Debian 源
RUN sed -i 's|deb.debian.org/debian|mirrors.aliyun.com/debian|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|security.debian.org|mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list.d/debian.sources

WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 升级pip并安装依赖
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY . .

# 创建日志目录并设置权限
RUN mkdir -p logs && chmod +x start.sh

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000 8501

# 设置环境变量
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["./start.sh"]
