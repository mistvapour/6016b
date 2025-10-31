#!/usr/bin/env python3
"""
RAG 服务最小骨架：
- 简单文本切片与倒排索引
- 基于词重叠的Top-K检索
- 简单评测占位（延迟/命中率）

说明：为便于立即运行，不依赖第三方库。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import time
import re


def _normalize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text)
    tokens = [t for t in text.split() if t]
    return tokens


@dataclass
class SearchHit:
    doc_id: int
    score: float
    snippet: str


class RAGService:
    def __init__(self) -> None:
        self.documents: List[str] = []
        self.inverted_index: Dict[str, List[int]] = {}

    def index(self, corpus: List[str]) -> None:
        self.documents = corpus
        self.inverted_index.clear()
        for idx, doc in enumerate(corpus):
            for token in set(_normalize(doc)):
                self.inverted_index.setdefault(token, []).append(idx)

    def query(self, query_text: str, top_k: int = 3) -> List[SearchHit]:
        if not self.documents:
            return []
        q_tokens = _normalize(query_text)
        candidate_scores: Dict[int, int] = {}
        for qt in set(q_tokens):
            for doc_id in self.inverted_index.get(qt, []):
                candidate_scores[doc_id] = candidate_scores.get(doc_id, 0) + 1
        ranked: List[Tuple[int, float]] = sorted(
            ((doc_id, score) for doc_id, score in candidate_scores.items()),
            key=lambda x: x[1], reverse=True,
        )
        hits: List[SearchHit] = []
        for doc_id, score in ranked[:top_k]:
            snippet = self.documents[doc_id][:200].replace("\n", " ")
            hits.append(SearchHit(doc_id=doc_id, score=float(score), snippet=snippet))
        return hits

    def evaluate(self, queries_with_refs: List[Tuple[str, int]], top_k: int = 3) -> Dict[str, float]:
        """
        简单评测：
        - latency_ms: 平均查询耗时
        - hit_at_k: Top-K 是否命中参考doc的比例
        """
        if not queries_with_refs:
            return {"latency_ms": 0.0, "hit_at_k": 0.0}

        total_ms = 0.0
        hits = 0
        for q, ref_id in queries_with_refs:
            t0 = time.time()
            results = self.query(q, top_k=top_k)
            total_ms += (time.time() - t0) * 1000.0
            if any(r.doc_id == ref_id for r in results):
                hits += 1
        return {
            "latency_ms": total_ms / len(queries_with_refs),
            "hit_at_k": hits / len(queries_with_refs),
        }


def simple_chunk(text: str, max_len: int = 800) -> List[str]:
    """极简切片：按段落/长度切片。"""
    parts: List[str] = []
    for para in re.split(r"\n\s*\n+", text):
        para = para.strip()
        if not para:
            continue
        while len(para) > max_len:
            parts.append(para[:max_len])
            para = para[max_len:]
        parts.append(para)
    return parts


__all__ = ["RAGService", "SearchHit", "simple_chunk"]


