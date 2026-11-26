import re
import io
import json
import base64
import asyncio
import httpx
import chromadb
from pathlib import Path
from typing import List, Optional
from PIL import Image

import config

BASE = Path(__file__).resolve().parent
RAG_DIR = BASE / "data" / "rag"
DOCS_DIR = RAG_DIR / "docs"
IMAGES_DIR = RAG_DIR / "images"
CACHE_DIR = RAG_DIR / "cache"
CHROMA_DIR = RAG_DIR / "chroma"
DESC_CACHE_PATH = CACHE_DIR / "image_descriptions.json"

for d in [RAG_DIR, DOCS_DIR, IMAGES_DIR, CACHE_DIR, CHROMA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DASHSCOPE_API_KEY = config.DASHSCOPE_API_KEY
EMBED_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
EMBED_MODEL = "text-embedding-v3"
VLM_MODEL = config.VLM_MODEL

if DASHSCOPE_API_KEY:
    print(f"[rag] DASHSCOPE_API_KEY 已加载：{DASHSCOPE_API_KEY[:8]}...")

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
COLLECTION_NAME = "docs"
MAX_TEXT_LEN = 6000

# 建索引时单次 embedding 的条数（DashScope 上限 25，留点余量）
EMBED_BATCH_SIZE = 10

IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

IMAGE_DESC_PROMPT = """你是软件界面截图描述助手。请用一句简短的话（不超过 80 字）描述这张截图的重点内容。

要求：
1. 说明这是什么软件的什么界面
2. 重点描述可交互的控件
3. 说明它们的位置
4. 不要描述颜色细节，不要评价
5. 直接输出描述

示例输出：
PyCharm 欢迎界面，左上角有蓝色 New Project 按钮，右上角有搜索图标
"""


# ============ Chroma ============
_chroma_client = None
_collection = None


def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ============ Embedding ============
async def get_embedding(text: str) -> Optional[List[float]]:
    if not text or not DASHSCOPE_API_KEY:
        return None
    text = text[:MAX_TEXT_LEN]
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": EMBED_MODEL, "input": [text]}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(EMBED_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as e:
        print(f"[rag] embedding 失败：{e}")
        return None


async def get_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """真正按批请求（旧实现是循环单条，9 篇文档要发几百次请求）。"""
    if not texts:
        return []

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    results: List[Optional[List[float]]] = []

    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = [t[:MAX_TEXT_LEN] for t in texts[start:start + EMBED_BATCH_SIZE]]
        payload = {"model": EMBED_MODEL, "input": batch}

        vectors = None
        for _ in range(3):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.post(EMBED_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    vectors = [d["embedding"] for d in resp.json()["data"]]
                    break
                print(f"[rag] embedding HTTP {resp.status_code}：{resp.text[:120]}")
            except Exception as e:
                print(f"[rag] embedding 异常：{e}")
            await asyncio.sleep(1)

        if vectors is None or len(vectors) != len(batch):
            results.extend([None] * len(batch))
        else:
            results.extend(vectors)

        print(f"[rag] embedding 进度：{min(start + EMBED_BATCH_SIZE, len(texts))}/{len(texts)}")

    return results


# ============ 图片描述 ============
def load_desc_cache() -> dict:
    if DESC_CACHE_PATH.exists():
        try:
            return json.loads(DESC_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_desc_cache(cache: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DESC_CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


async def describe_image(img_path: Path) -> str:
    if not img_path.exists() or not DASHSCOPE_API_KEY:
        return ""
    try:
        img = Image.open(img_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        if max(img.size) > 1024:
            r = 1024 / max(img.size)
            img = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"[rag] 读取图片失败 {img_path.name}：{e}")
        return ""

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": VLM_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": IMAGE_DESC_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            ],
        }],
        "temperature": 0.1,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(CHAT_URL, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        return content.strip('"').strip("'").strip()
    except Exception as e:
        print(f"[rag] 生成图片描述失败 {img_path.name}：{e}")
        return ""


async def process_document_async(text: str, doc_name: str, desc_cache: dict) -> str:
    matches = list(IMG_PATTERN.finditer(text))
    if not matches:
        return text

    tasks = []
    for m in matches:
        img_rel = m.group(2)
        img_name = Path(img_rel).name
        img_path = IMAGES_DIR / img_name
        if img_name in desc_cache:
            continue
        tasks.append((img_name, img_path))

    if tasks:
        sem = asyncio.Semaphore(3)
        async def safe_describe(name, path):
            async with sem:
                return await describe_image(path)
        results = await asyncio.gather(*[safe_describe(n, p) for n, p in tasks])
        for (img_name, _), desc in zip(tasks, results):
            desc_cache[img_name] = desc

    def replace(match):
        img_rel = match.group(2)
        img_name = Path(img_rel).name
        desc = desc_cache.get(img_name, "")
        if desc:
            return f"\n【图片说明】{desc}\n【图片文件】{img_name}\n"
        return f"\n【图片文件】{img_name}\n"

    return IMG_PATTERN.sub(replace, text)


# ============ 切片 ============
def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= chunk_size:
            current = (current + "\n\n" + p).strip() if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) > chunk_size:
                for i in range(0, len(p), chunk_size - overlap):
                    chunks.append(p[i:i + chunk_size])
                current = ""
            else:
                current = p
    if current:
        chunks.append(current)
    return chunks


def extract_images_from_chunk(chunk: str) -> List[str]:
    results = []
    for m in re.finditer(r'【图片文件】(.+?)(?:\n|【|$)', chunk):
        name = m.group(1).strip()
        if name:
            results.append(Path(name).name)
    return results


# ============ 构建索引 ============
async def build_index():
    files = list(DOCS_DIR.glob("*.md")) + list(DOCS_DIR.glob("*.txt"))
    if not files:
        print(f"[rag] 没有文档")
        return

    desc_cache = load_desc_cache()
    all_chunks = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        text_with_desc = await process_document_async(text, f.name, desc_cache)
        chunks = split_text(text_with_desc)
        for i, c in enumerate(chunks):
            images = extract_images_from_chunk(c)
            all_chunks.append({
                "source": f.name, "chunk_index": i,
                "content": c, "images": images,
            })

    save_desc_cache(desc_cache)
    print(f"[rag] 共 {len(all_chunks)} 个片段，开始 embedding...")
    texts = [c["content"] for c in all_chunks]
    embeddings = await get_embeddings_batch(texts)

    valid = []
    for c, emb in zip(all_chunks, embeddings):
        if emb is None:
            continue
        c["embedding"] = emb
        valid.append(c)

    print(f"[rag] embedding 成功：{len(valid)}/{len(all_chunks)}")
    if not valid:
        return

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"},
    )

    for i in range(0, len(valid), 50):
        batch = valid[i:i + 50]
        collection.add(
            documents=[c["content"] for c in batch],
            embeddings=[c["embedding"] for c in batch],
            metadatas=[{
                "source": c["source"],
                "chunk_index": c["chunk_index"],
                "images": ",".join(c["images"]),
            } for c in batch],
            ids=[f"{c['source']}_{c['chunk_index']}" for c in batch],
        )
    print(f"[rag] 已存入 Chroma：{len(valid)} 个片段")


# ============ 检索 ============
async def retrieve(query: str, top_k: int = 3, min_score: Optional[float] = None) -> List[dict]:
    if min_score is None:
        min_score = config.RAG_MIN_SCORE

    try:
        collection = get_collection()
        if collection.count() == 0:
            return []
    except Exception as e:
        print(f"[rag] 打开索引失败：{e}")
        return []

    q_emb = await get_embedding(query)
    if q_emb is None:
        return []

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=max(1, top_k),
        include=["documents", "metadatas", "distances"],
    )

    out = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, dists):
        similarity = 1 - float(dist)
        if similarity < min_score:
            continue
        imgs = (meta or {}).get("images", "")
        out.append({
            "source": (meta or {}).get("source", "unknown"),
            "content": doc,
            "images": imgs.split(",") if imgs else [],
            "score": round(similarity, 3),
        })

    out.sort(key=lambda r: -r["score"])
    return out


async def retrieve_relevant(query: str, top_k: int = 3) -> List[dict]:
    """
    只做一次阈值过滤。
    旧实现还有一层「用 OCR 文本和片段算相似度再筛一遍」，实测既拖慢速度，
    又会把真正相关的片段误杀，已移除。
    """
    if not query.strip():
        return []

    results = await retrieve(query, top_k=top_k)
    if not results:
        return []

    # 只保留和最佳结果接近的，避免把"沾边"的片段一起塞进提示词
    best = results[0]["score"]
    return [r for r in results if best - r["score"] <= 0.08]


def format_rag_context(results: List[dict]) -> str:
    if not results:
        return "（未检索到有效内容）"
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"【文档 {i}】来源：{r['source']}（相似度：{r['score']}）\n{r['content']}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    import asyncio
    async def main():
        print("构建索引...")
        await build_index()
    asyncio.run(main())