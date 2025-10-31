#!/usr/bin/env python3
from pathlib import Path
from backend.table_parser.pymupdf_tables import parse_tables_from_pdf


def main():
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    if not Path(pdf_path).exists():
        print("PDF不存在:", pdf_path)
        return
    tables = parse_tables_from_pdf(pdf_path)
    print("候选表格页数:", len(tables))
    for t in tables[:3]:
        print("- page:", t["page"], " rows:", len(t["rows"]))
        if t["rows"]:
            print("  header:", t["rows"][0])
            print("  sample:", t["rows"][1:4])


if __name__ == "__main__":
    main()


