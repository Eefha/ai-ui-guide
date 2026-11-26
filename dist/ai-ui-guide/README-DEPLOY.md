# 部署到阿里云服务器

这个包解压后在 Linux 上一条命令就能跑起来。整套服务是**单容器**：FastAPI 同时提供
接口和前端页面（同源，无跨域问题），数据落在宿主机的 `backend/data` 目录。

---

## 一、服务器要求

| 项 | 建议 |
| --- | --- |
| 系统 | Alibaba Cloud Linux 3 / Ubuntu 22.04 / Debian 12，x86_64 |
| 配置 | 2 核 2G 起步（构建时内存峰值约 1G），磁盘 20G |
| 软件 | Docker 20.10+ 与 compose 插件 |

没装 Docker 的话：

```bash
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
systemctl enable --now docker
```

---

## 二、上传

本地（Windows PowerShell / macOS 终端）：

```bash
# 把 <公网IP> 换成你的 ECS 公网地址
scp ai-ui-guide-20261105.tar.gz root@<公网IP>:/opt/
ssh root@<公网IP>
cd /opt && tar -xzf ai-ui-guide-20261105.tar.gz && cd ai-ui-guide
```

> 包里**不含** `.env`（里面是密钥，不跟着压缩包走）。用下面任一方式补上：
>
> ```bash
> # 方式 A：从本机直接传（推荐）
> scp backend/.env root@<公网IP>:/opt/ai-ui-guide/backend/.env
>
> # 方式 B：在服务器上按模板填
> cp backend/.env.example backend/.env && vim backend/.env
> ```

---

## 三、配置 `backend/.env`

只有第一项是硬性必填，其余不填会优雅降级：

| 变量 | 必填 | 不填的后果 |
| --- | --- | --- |
| `DASHSCOPE_API_KEY` | **是** | 服务起得来，但所有分析请求失败 |
| `JWT_SECRET` | 是 | 用默认值也能跑，但登录令牌可被伪造，建议 `openssl rand -hex 32` |
| `ALIBABA_CLOUD_ACCESS_KEY_ID` / `_SECRET` | 否 | 跳过 OCR，定位准确率下降 |
| `BAIDU_SEARCH_API_KEY` | 否 | 跳过联网搜索 |
| `SMTP_USER` / `SMTP_PASSWORD` | 否 | 邮箱验证码发不出，只能游客使用 |

---

## 四、启动

```bash
bash deploy.sh              # 默认 8080 端口
APP_PORT=80 bash deploy.sh  # 想直接占 80
```

脚本会依次完成：检查配置 → 构建镜像 → 启动容器 → 轮询 `/health` → 打印访问地址。
首次构建 3~8 分钟（装依赖占大头），之后改代码再执行只重建代码层，很快。

看到 `部署完成` 就能访问 `http://<公网IP>:8080`。

**这一步最容易漏：阿里云控制台 → 安全组 → 入方向，放行对应端口（8080 或 80）。**

---

## 五、日常运维

```bash
docker compose logs -f --tail=100    # 看日志
docker compose restart               # 重启
docker compose down                  # 停止
bash deploy.sh                       # 改了代码后重新构建上线
```

**备份**（会话记录、上传的截图、知识库都在 `backend/data`）：

```bash
tar -czf ~/backup-$(date +%F).tar.gz backend/data
```

**迁移**：把 `backend/data` 拷到新机器同一位置即可，其余都是无状态代码。

---

## 六、绑域名 + HTTPS（可选）

容器只监听 8080，前面挂 Nginx 更省心（也能顺便做限流）。在宿主机：

```nginx
server {
    listen 80;
    server_name guide.example.com;

    client_max_body_size 20m;   # 截图可能几 MB，默认 1m 会 413

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;   # 模型分析最慢要 10s+，别用默认 60s
    }
}
```

证书用 `certbot --nginx -d guide.example.com` 一条命令搞定。镜像启动时带了
`--proxy-headers`，Nginx 传来的真实 IP 会被正确识别。

绑了域名后，安全组只需放行 80/443，8080 可以只对本机开放。

---

## 七、常见问题

**`docker compose up` 卡在拉取 `python:3.11-slim` 或超时**
国内服务器拉 Docker Hub 不稳定，配一下加速器（阿里云容器镜像服务控制台可获取专属地址）：

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{ "registry-mirrors": ["https://<你的ID>.mirror.aliyuncs.com"] }
EOF
systemctl daemon-reload && systemctl restart docker
```

**构建报 `pip install` 失败**
Dockerfile 用的是阿里云 PyPI 源。如果服务器在境外，把 `-i https://mirrors.aliyun.com/pypi/simple/`
换成官方源即可。

**容器起来了但页面报错 / `/health` 打不开**

```bash
docker compose logs --tail=80
```
多数是 `.env` 没放对位置（必须在 `backend/.env`）或 `DASHSCOPE_API_KEY` 写错。

**时间显示差 8 小时**
镜像里已设 `TZ=Asia/Shanghai`，如果你改过 compose，别把 `TZ` 删掉。

**知识库检索不到内容**
包里带了一份建好的索引（`backend/data/rag/chroma`）。极少数情况下跨平台索引读不了，
删掉重建即可：

```bash
rm -rf backend/data/rag/chroma
docker compose exec app python rag.py    # 会调 embedding 与图片描述接口，有少量费用
```

**内存不够（1G 机器）**
容器常驻约 300~500M，构建时更高。1G 机器建议临时开 swap 再构建，或升到 2G。

---

## 八、不想用 Docker？

也可以直接跑。要求 Python 3.11：

```bash
cd /opt/ai-ui-guide
python3.11 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
cd backend && ../.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

长期跑建议交给 systemd（`Restart=always`），或者仍然用 Docker，省事。

---

## 九、包内容

```
ai-ui-guide/
├── deploy.sh                 一键部署脚本
├── docker-compose.yml        容器编排（端口、健康检查、日志轮转、数据挂载）
├── .dockerignore             构建时排除 .venv / dev / 密钥
├── README-DEPLOY.md          本文件
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt      已锁版本
│   ├── main.py               FastAPI 入口，同时托管前端
│   ├── agent_graph.py        分析主流程
│   ├── prompts/              提示词模板（改文案只动这里）
│   ├── .env.example          配置模板
│   └── data/
│       └── rag/              知识库文档、图片与已建好的向量索引
└── frontend/
    └── index.html            单文件前端
```

不含：`.venv`（Windows 虚拟环境，Linux 不可用）、`dev/`（开发脚本）、
`md文件转换/`（文档转换中间产物）、本机会话数据与 `.env`。
