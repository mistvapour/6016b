#!/usr/bin/env python3
"""
向量RAG服务（轻量级，不强制依赖第三方向量库）
- 使用简单的TF-IDF向量作为Embedding占位
- 支持后续替换为真实Embedding模型
- 实现Top-K检索与评测接口
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict
import time
import math
from collections import Counter


def _tfidf_embedding(text: str, vocab_tf: Dict[str, int], doc_count: int, df: Dict[str, int]) -> List[float]:
    """TF-IDF作为简单Embedding占位"""
    tokens = text.lower().split()
    tf = Counter(tokens)
    vec = []
    for word in vocab_tf:
        tf_score = tf.get(word, 0) / max(len(tokens), 1)
        idf_score = math.log((doc_count + 1) / (df.get(word, 0) + 1)) if df.get(word, 0) > 0 else 0
        vec.append(tf_score * idf_score)
    return vec


def _cosine_sim(a: List[float], b: List[float]) -> float:
    """余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class SearchHit:
    doc_id: int
    score: float
    snippet: str


class VectorRAGService:
    def __init__(self, embedding_func=None):
        self.documents: List[str] = []
        self.vectors: List[List[float]] = []
        self.vocab_tf: Dict[str, int] = {}
        self.df: Dict[str, int] = {}
        self.doc_count = 0
        
    def index(self, corpus: List[str]) -> None:
        self.documents = corpus
        self.doc_count = len(corpus)
        
        # 建立词汇表与DF
        self.vocab_tf = {}
        self.df = {}
        for doc in corpus:
            tokens = set(t.lower() for t in doc.split())
            for t in tokens:
                self.vocab_tf[t] = self.vocab_tf.get(t, 0) + 1
            for t in tokens:
                self.df[t] = self.df.get(t, 0) + 1
        
        # 为每个文档生成向量
        self.vectors = []
        for doc in corpus:
            vec = _tfidf_embedding(doc, self.vocab_tf, self.doc_count, self.df)
            self.vectors.append(vec)
    
    def query(self, query_text: str, top_k: int = 3) -> List[SearchHit]:
        if not self.documents:
            return []
        
        q_vec = _tfidf_embedding(query_text, self.vocab_tf, self.doc_count, self.df)
        
        scores = []
        for idx, d_vec in enumerate(self.vectors):
            score = _cosine_sim(q_vec, d_vec)
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        hits = []
        for idx, score in scores[:top_k]:
            snippet = self.documents[idx][:200].replace("\n", " ")
            hits.append(SearchHit(doc_id=idx, score=score, snippet=snippet))
        
        return hits
    
    def evaluate(self, queries_with_refs: List[Tuple[str, int]], top_k: int = 3) -> Dict[str, float]:
        """
        评测：平均延迟与Top-K命中率
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


__all__ = ["VectorRAGService", "SearchHit"]

