# AI 点点工具（ai-ui-guide）

> 上传一张软件截图 + 一句话目标，系统直接在图上圈出「下一步点这里」的位置；当前界面找不到时诚实地说找不到并给建议，绝不编造坐标。

一个面向「软件操作引导」的 AI 应用。传统教程给一堆文字步骤，用户对着自己的截图仍不知道点哪；本项目让视觉模型理解截图，输出可点击的相对坐标，前端按比例把红框贴回原图。

## 技术栈

- **后端**：FastAPI + LangGraph + SQLite（WAL）+ Chroma 本地向量库
- **前端**：单文件 `frontend/index.html`，零构建，百分比定位画框
- **模型**：阿里云百炼 qwen3-vl-plus（视觉理解）、text-embedding-v3（向量）
- **外部能力**：阿里云 OCR、百度千帆联网搜索、SMTP 邮箱验证码
- **部署**：单容器 Docker，`backend/data` 挂载宿主机即可迁移

## 核心设计

### 1. LangGraph 六节点编排

```
check_task → gather_context → call_model → validate →(retry)→ finalize
```

- `check_task`：判定是否换任务（关键词 / 与旧目标相似度 < 0.55）
- `gather_context`：OCR 与 RAG 并发；带截图默认不联网
- `call_model`：按「有无图 / 有无文字」选提示词模板
- `validate`：坐标归一化 + 结构校验
- `retry`：仅在「要圈位置且坐标无效」时、以 temperature=0 重试一次
- `finalize`：两次仍失败则降级为文字回答

### 2. 纵深防御：模型输出不可信怎么办

六道防线，从提示词到出口逐层兜底：

1. **提示词约束**——诚实原则，允许模型输出「找不到」
2. **容错解析**——代码块、中文标点、尾逗号修复
3. **双重校验**——reply_type 规范化 + bbox 五种容错
4. **受控重试**——只重试一次，两次用同一校验标准
5. **强制降级**——失败转文字，绝不给空框
6. **出口兜底**——前后端各再校验一次

### 3. 坐标归一化（`backend/bbox.py`）

无论模型吐相对坐标、像素坐标还是对角点，统一出口为 `[x, y, w, h]` 的 0~1 相对值。前端用 CSS 百分比定位，图片任意缩放都能贴合，无需监听 resize。

### 4. 提示词分层

`prompts/system_core.txt` 放恒定铁律（改行为只改这一个文件，且前缀稳定可命中缓存）；`user_action / user_ask / user_text / user_retry` 四个模板按场景选择，占位符由代码注入，缺变量直接抛错而非静默留空。

## 目录结构

```
frontend/index.html          前端单文件（UI + 全部 JS 逻辑）
backend/
  main.py                    FastAPI 入口：认证、会话、/analyze
  config.py                  环境变量与阈值唯一来源
  agent_graph.py             LangGraph 六节点主流程
  prompt_builder.py          提示词拼装
  prompts/                   system_core + 四个 user 模板 + loader
  bbox.py                    坐标归一化与合法性校验
  llm_utils.py               图片压缩、模型调用、JSON 容错解析
  ocr.py / rag.py / web_search.py / embeddings.py
  storage.py                 SQLite 五表：用户/验证码/会话/消息/进度
  auth.py                    邮箱验证码 + JWT + 游客身份
  data/                      运行时数据（不入库，已 gitignore）
docker-compose.yml / Dockerfile / deploy.sh
```

## 快速开始

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # 填入 DashScope / OCR / SMTP 等密钥
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000`。RAG 知识库首次使用需执行 `python rag.py` 建索引。

详细部署见 [README-DEPLOY.md](README-DEPLOY.md)，后端细节见 [backend/README.md](backend/README.md)。

## 安全说明

`.env`（真实密钥）、`data/`（用户会话与向量库）、`.venv/` 均已加入 `.gitignore`，不会进入版本库。仓库中只保留 `.env.example` 模板。
