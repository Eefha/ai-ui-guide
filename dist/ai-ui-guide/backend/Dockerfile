# 构建上下文是项目根目录（见 docker-compose.yml 的 context: .）
# 手动构建：docker build -f backend/Dockerfile -t ai-ui-guide:latest .
FROM python:3.11-slim

# TZ 必须设，否则容器内 datetime.now() 是 UTC，消息时间会差 8 小时
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Shanghai

WORKDIR /workspace

# 阿里云 apt 源 + curl（healthcheck 用）+ tzdata（TZ 需要时区库）
RUN set -eux; \
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/debian.sources; do \
        if [ -f "$f" ]; then \
            sed -i 's|deb.debian.org|mirrors.aliyun.com|g; s|security.debian.org|mirrors.aliyun.com|g' "$f"; \
        fi; \
    done; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl tzdata; \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime; \
    echo $TZ > /etc/timezone; \
    rm -rf /var/lib/apt/lists/*

# 依赖单独一层，改代码不必重装依赖
COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install -r /workspace/backend/requirements.txt \
        -i https://mirrors.aliyun.com/pypi/simple/

COPY backend /workspace/backend
COPY frontend /workspace/frontend

# 数据目录；知识库由 volume 挂载提供，这里只保证目录存在
RUN mkdir -p /workspace/backend/data/rag/images /workspace/backend/data/rag/docs

WORKDIR /workspace/backend

EXPOSE 8000

# --proxy-headers 让 Nginx / SLB 反代时能拿到真实客户端 IP 与协议
CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
