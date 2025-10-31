#!/usr/bin/env python3
from pathlib import Path
import json
from backend.table_parser.pymupdf_tables import parse_tables_from_pdf
from backend.table_parser.normalize import normalize_tables


def main():
    pdf_path = r"C:\Users\Administrator\Documents\毕业论文\代码\前端\6016-app\华东师范大学硕_博_士论文LaTex模板_\公开版llm-数据链消息模拟客户端开发与测试250716(3).pdf"
    out_dir = Path("table_dict_output")
    out_dir.mkdir(exist_ok=True)

    tables = parse_tables_from_pdf(pdf_path)
    norm = normalize_tables(tables)

    out_file = out_dir / "fields_candidate.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(norm, f, ensure_ascii=False, indent=2)

    print("页数:", len(norm))
    if norm:
        print("示例:", json.dumps(norm[0], ensure_ascii=False)[:400], "...")
        print("已导出:", out_file)


if __name__ == "__main__":
    main()


