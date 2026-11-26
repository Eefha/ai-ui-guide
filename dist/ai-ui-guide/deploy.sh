#!/usr/bin/env bash
# 一键部署：构建镜像 + 启动容器 + 健康检查
# 用法：bash deploy.sh          默认映射到 8080
#      APP_PORT=80 bash deploy.sh   映射到 80
set -euo pipefail
cd "$(dirname "$0")"

PORT="${APP_PORT:-8080}"
say() { printf "\n\033[1;36m==> %s\033[0m\n" "$*"; }
die() { printf "\n\033[1;31m[错误] %s\033[0m\n" "$*" >&2; exit 1; }

# ---------- 1. 配置文件 ----------
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  cat <<EOF
未找到 backend/.env，已从 .env.example 生成一份。请先填这几项再运行：

  DASHSCOPE_API_KEY                       必填，阿里云百炼 API Key
  ALIBABA_CLOUD_ACCESS_KEY_ID/_SECRET     选填，不填则跳过 OCR
  JWT_SECRET                              必填，建议 openssl rand -hex 32
  SMTP_USER / SMTP_PASSWORD               选填，不填则邮箱验证码不可用

编辑：vim $(pwd)/backend/.env
填好后重新执行：bash deploy.sh
EOF
  exit 1
fi

# ---------- 2. 环境检查 ----------
command -v docker >/dev/null 2>&1 || die "未安装 Docker。可执行：
  curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
  systemctl enable --now docker"

docker info >/dev/null 2>&1 || die "Docker 守护进程没运行：systemctl start docker"

if docker compose version >/dev/null 2>&1; then
  DC=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  DC=(docker-compose)
else
  die "缺少 compose 插件。Alibaba Cloud Linux/CentOS: dnf install -y docker-compose-plugin
Ubuntu/Debian: apt install -y docker-compose-plugin"
fi

mkdir -p backend/data/rag/images backend/data/rag/docs

# ---------- 3. 构建并启动 ----------
say "构建镜像（首次约 3~8 分钟）"
APP_PORT="$PORT" "${DC[@]}" up -d --build

# ---------- 4. 等待就绪 ----------
say "等待服务就绪"
for _ in $(seq 1 40); do
  if curl -fsS --noproxy '*' "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "健康检查："
    curl -s --noproxy '*' "http://127.0.0.1:${PORT}/health"; echo
    IP=$(curl -s --max-time 3 --noproxy '*' https://api.ipify.org 2>/dev/null || echo "<服务器公网IP>")
    cat <<EOF

部署完成。
  访问      http://${IP}:${PORT}
  看日志    ${DC[*]} logs -f --tail=100
  重启      ${DC[*]} restart
  停止      ${DC[*]} down
  改代码后  bash deploy.sh   （会重新构建）

如果打不开，先确认阿里云安全组已放行 ${PORT} 端口。
EOF
    exit 0
  fi
  sleep 3
done

echo "--- 最近 60 行日志 ---"
"${DC[@]}" logs --tail=60
die "服务未通过健康检查，请把上面的日志发出来排查"
