# AI 软件操作引导（后端）

用户上传软件截图并说明想做什么，模型在图上圈出「下一步点这里」的位置，或直接回答问题。

## 目录结构

```
backend/
├─ main.py            FastAPI 入口：认证、会话、/analyze
├─ config.py          所有环境变量与可调参数的唯一来源
├─ agent_graph.py     LangGraph 编排：判断新任务 → 收集上下文 → 调模型 → 校验 → 重试/降级
├─ prompt_builder.py  把状态拼成 (system, user)，按「有无图/有无话」选模板
├─ prompts/           提示词正文（改这里就能调行为，不用碰代码）
│   ├─ loader.py      $变量渲染，缺变量直接报错
│   ├─ system_core.txt    角色、铁律、坐标规范、诚实原则、输出格式
│   ├─ user_action.txt    有截图 + 有目标
│   ├─ user_ask.txt       有截图 + 没说话
│   ├─ user_text.txt      纯文字提问
│   └─ user_retry.txt     第一次没给出有效坐标时的二次定位
├─ llm_utils.py       图片压缩、调模型、JSON 解析
├─ bbox.py            坐标归一化（像素→相对、对角→宽高、扩小框、越界裁剪）
├─ ocr.py             阿里云 OCR，输出带坐标的候选文字清单
├─ rag.py             Chroma 向量检索（建索引用 `python rag.py`）
├─ web_search.py      百度千帆搜索 + 相关性过滤
├─ embeddings.py      文本向量与余弦相似度
├─ storage.py         SQLite：用户、会话、消息、进度
├─ auth.py            邮箱验证码 + JWT + 游客身份
└─ dev/               调试脚本与测试素材，不参与线上运行
```

## 一次请求的链路

```
用户发图+目标
  └─ check_task       是否换任务（关键词 / 与旧目标相似度 < 0.55）
  └─ gather_context   OCR 与 RAG 并发；带截图默认不联网
  └─ call_model       system_core + 对应 user_xxx 模板
  └─ validate         bbox 归一化；不可用就标记
       ├─ retry       只有「要圈位置」且坐标无效时才重试一次
       └─ finalize    还是不行 → 降级成文字回答，绝不给空框
```

## 调提示词

只改 `prompts/*.txt` 即可，不用动代码。三个原则：

1. **system 里放恒定规则**（角色、坐标规范、输出格式），user 模板里放这一轮的数据。
   这样 system 前缀稳定，命中缓存也更便宜。
2. 模板里的 `$变量` 必须全部被 `prompt_builder.py` 传入，漏了会直接抛错，
   不会像以前那样静默留空。
3. 改完用 `dev/smoke_test.py` 跑一遍四种典型场景，看模型实际输出。

## 自测

```bash
# 坐标归一化的单元测试（不花钱）
.venv\Scripts\python.exe dev\test_bbox.py

# 端到端跑 Agent，不经过 HTTP
.venv\Scripts\python.exe dev\smoke_test.py
.venv\Scripts\python.exe dev\smoke_test.py 图片1.png "怎么运行这个程序"

# 起服务
.venv\Scripts\python.exe -m uvicorn main:app --port 8000
```

## 虚拟环境说明（为什么 .venv 还能再瘦）

`.venv` 里曾装过一套本地图标检测的依赖（torch / torchvision / modelscope /
opencv-python-headless / scikit-image / scipy / sympy / kubernetes / onnxruntime），
那条路线已经废弃，代码与 `dev/` 脚本都不再引用，已卸载，占用从 1.7G 降到约 510M。

两点需要知道：

- **保留 `PyQt5`**：它是 `labelImg`（图标标注工具）的运行依赖。确认不再标注后，
  执行 `pip uninstall -y PyQt5 labelImg` 还能再省约 150M。
- **`pip check` 会报两条告警**：`chromadb` 声明依赖 `kubernetes`（仅分布式模式用到）
  和 `onnxruntime`（仅默认 embedding function 用到）。本项目始终自己算向量并显式传入，
  两条路径都不会走到，本地检索已实测正常。若以后要用 chromadb 自带的 embedding，
  先 `pip install onnxruntime`。

## 可调参数

见 `config.py` 与 `.env.example`。常改的几个：

| 参数 | 作用 | 默认 |
| --- | --- | --- |
| `QWEN_MODEL` | 主模型（omni 系列慢 5~10 倍，不建议用于纯截图任务） | qwen3-vl-plus |
| `IMAGE_MAX_SIDE` | 送模型前的图片长边 | 1600 |
| `RAG_MIN_SCORE` | 知识库相似度门槛，太高等于没有知识库 | 0.65 |
| `WEB_SEARCH_WITH_IMAGE` | 带截图时是否联网，默认关闭以免拖慢 | false |
| `MIN_BBOX_SIDE` | 坐标框最小边长，防止模型给"点"级小框 | 0.028 |
| `MAX_BBOX_AREA` | 坐标框面积上限，超过就当作"框住了整块面板"并拒绝 | 0.45 |
