#!/usr/bin/env python3
from pathlib import Path
from backend.rag_service.vector_rag import VectorRAGService
from backend.rag_service.service import simple_chunk

def main():
    print("== 向量RAG演示 ==")
    
    # 读取PDF提取文本
    text_file = Path("pdf_text_output/extracted_text.txt")
    if not text_file.exists():
        print("请先运行 extract_pdf_text.py")
        return
    
    text = text_file.read_text(encoding='utf-8', errors='ignore')
    
    # 切片并索引
    chunks = simple_chunk(text, max_len=600)
    print(f"文档切片数: {len(chunks)}")
    
    rag = VectorRAGService()
    rag.index(chunks)
    
    # 查询
    queries = [
        "Link 16 消息标准",
        "数据链消息生成",
        "LLM RAG 解析",
        "消息字典自动生成",
    ]
    
    print("\n[查询结果]")
    for q in queries:
        hits = rag.query(q, top_k=3)
        print(f"\n查询: {q}")
        for h in hits:
            print(f"  doc={h.doc_id} score={h.score:.3f} snippet={h.snippet[:80]}")
    
    # 简单评测
    test_cases = [
        ("Link 16", 0),
        ("消息生成", 1),
        ("标准文档", 2),
    ]
    
    eval_result = rag.evaluate(test_cases, top_k=3)
    print(f"\n[评测结果]")
    print(f"平均延迟: {eval_result['latency_ms']:.2f} ms")
    print(f"Top-3命中率: {eval_result['hit_at_k']:.2%}")
    
    print("\n== 完成 ==")

if __name__ == "__main__":
    main()

