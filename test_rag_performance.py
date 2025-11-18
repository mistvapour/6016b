#!/usr/bin/env python3
"""
RAG性能测试脚本
验证是否达到1500ms延迟和90%命中率要求
"""
from pathlib import Path
import time
from backend.rag_service.vector_rag import VectorRAGService
from backend.rag_service.service import simple_chunk


def test_rag_performance():
    """测试RAG性能指标"""
    print("="*60)
    print("RAG性能测试")
    print("="*60)
    
    # 读取PDF提取文本
    text_file = Path("pdf_text_output/extracted_text.txt")
    if not text_file.exists():
        print("❌ 未找到提取的文本文件，请先运行 extract_pdf_text.py")
        return
    
    print("\n📄 加载文档...")
    text = text_file.read_text(encoding='utf-8', errors='ignore')
    print(f"   文档长度: {len(text)} 字符")
    
    # 切片并索引
    print("\n🔪 文档切片...")
    chunks = simple_chunk(text, max_len=600)
    print(f"   切片数量: {len(chunks)}")
    
    # 创建RAG服务
    print("\n🔍 构建索引...")
    rag = VectorRAGService()
    start_time = time.time()
    rag.index(chunks)
    index_time = time.time() - start_time
    print(f"   索引构建时间: {index_time:.2f} 秒")
    
    # 准备测试查询
    test_queries = [
        ("Link 16 消息标准", 0),
        ("数据链消息生成", 1),
        ("J系列消息定义", 2),
        ("位段信息解析", 3),
        ("字段约束条件", 4),
        ("消息字典生成", 5),
        ("PDF文档处理", 6),
        ("语义检索", 7),
        ("向量化索引", 8),
        ("Top-K检索", 9),
    ]
    
    print(f"\n📊 执行性能测试（{len(test_queries)}个查询）...")
    
    total_latency = 0.0
    hits = 0
    
    for i, (query, ref_id) in enumerate(test_queries, 1):
        # 测量查询延迟
        t0 = time.time()
        results = rag.query(query, top_k=3)
        latency = (time.time() - t0) * 1000.0  # 转换为毫秒
        total_latency += latency
        
        # 检查是否命中
        hit = any(r.doc_id == ref_id for r in results)
        if hit:
            hits += 1
        
        status = "✅" if hit else "❌"
        print(f"   {i}. {query:20s} | 延迟: {latency:6.2f}ms | {status}")
    
    # 计算平均指标
    avg_latency = total_latency / len(test_queries)
    hit_rate = hits / len(test_queries)
    
    print("\n" + "="*60)
    print("📈 性能测试结果")
    print("="*60)
    print(f"平均检索延迟: {avg_latency:.2f} ms")
    print(f"Top-3命中率: {hit_rate:.2%}")
    print(f"命中数量: {hits}/{len(test_queries)}")
    
    # 验证是否达标
    print("\n" + "="*60)
    print("✅ 达标情况")
    print("="*60)
    
    latency_ok = avg_latency <= 1500.0
    hit_rate_ok = hit_rate >= 0.90
    
    print(f"延迟要求（≤1500ms）: {'✅ 达标' if latency_ok else '❌ 未达标'}")
    print(f"命中率要求（≥90%）: {'✅ 达标' if hit_rate_ok else '❌ 未达标'}")
    
    if latency_ok and hit_rate_ok:
        print("\n🎉 所有性能指标均已达标！")
    else:
        print("\n⚠️  部分指标未达标，建议：")
        if not latency_ok:
            print("   - 优化查询算法")
            print("   - 使用真实Embedding模型（如sentence-transformers）")
            print("   - 使用向量数据库（如FAISS）加速检索")
        if not hit_rate_ok:
            print("   - 优化文档切片策略")
            print("   - 使用更好的Embedding模型")
            print("   - 调整Top-K值或检索算法")
    
    return {
        "avg_latency_ms": avg_latency,
        "hit_rate": hit_rate,
        "latency_ok": latency_ok,
        "hit_rate_ok": hit_rate_ok,
        "total_queries": len(test_queries),
        "hits": hits
    }


if __name__ == "__main__":
    try:
        results = test_rag_performance()
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

