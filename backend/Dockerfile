FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 优化依赖安装缓存策略:
# 1. 先单独复制 requirements.txt
# 2. 安装依赖(这一层会被缓存,除非 requirements.txt 变化)
# 3. 最后复制源代码(代码变化不会影响依赖层缓存)
COPY requirements.txt .

# 使用固定的 pip 版本并安装依赖
# --no-cache-dir: 不缓存下载的包,减小镜像体积
RUN pip install --no-cache-dir --upgrade pip==24.0 -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip list > /app/installed_packages.txt

# 复制应用代码(放在依赖安装之后,这样代码变化不会导致重新安装依赖)
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# 使用更健壮的启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
