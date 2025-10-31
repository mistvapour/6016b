#!/usr/bin/env python3
"""
最小P0演示：
- 使用提取的PDF文本做RAG索引并检索
- 从文本中解析“类表格段”
- 构造一条消息定义，演示JSON/XML互转
"""
from pathlib import Path

from backend.rag_service.service import RAGService, simple_chunk
from backend.table_parser.prototype import parse_tables_from_text
from backend.schema.message_definition import MessageDefinition, MessageField, FieldConstraint


def main():
    print("== P0最小演示 ==")

    # 1) 读取前面生成的提取文本
    text_file = Path("pdf_text_output/extracted_text.txt")
    if not text_file.exists():
        print("未找到 pdf_text_output/extracted_text.txt，请先运行 extract_pdf_text.py")
        return
    text = text_file.read_text(encoding="utf-8", errors="ignore")

    # 2) RAG 索引与查询
    rag = RAGService()
    chunks = simple_chunk(text, max_len=600)
    rag.index(chunks)
    q = "Link 16 消息 标准 解析"
    hits = rag.query(q, top_k=3)
    print("\n[RAG 查询结果]")
    for h in hits:
        print(f"doc={h.doc_id} score={h.score} snippet={h.snippet[:80]}...")

    # 3) 表格解析原型
    tables = parse_tables_from_text(text)
    print(f"\n[表格解析原型] 检出块数: {len(tables)}")
    if tables:
        print(f"示例前3行: {tables[0][:3]}")

    # 4) 消息定义 schema 与 JSON/XML 互转
    msg = MessageDefinition(
        label="J10.2",
        title="Weapon Status Message",
        fields=[
            MessageField(
                name="WeaponStatus", dtype="enum", units=None, description="Current weapon status",
                bits=[0,5], constraint=FieldConstraint(required=True, enum=["Safe","Armed","Firing"]) ),
            MessageField(
                name="Range", dtype="uint", units="m", description="Target range",
                bits=[16,31], constraint=FieldConstraint(min_value=0, max_value=100000) ),
        ],
    )
    json_str = msg.to_json()
    xml_str = msg.to_xml()
    print("\n[消息定义 JSON]\n", json_str)
    print("\n[消息定义 XML]\n", xml_str)

    # 回读校验
    msg2 = MessageDefinition.from_json(json_str)
    msg3 = MessageDefinition.from_xml(xml_str)
    assert msg2.label == msg.label and msg3.title == msg.title
    print("\n互转校验通过")

    print("\n== 演示完成 ==")


if __name__ == "__main__":
    main()


