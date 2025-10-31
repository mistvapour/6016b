#!/usr/bin/env python3
from pathlib import Path
import json
from backend.converters.table_to_message import tables_to_message, simple_validate_coverage


def main():
    in_file = Path("table_dict_output/fields_candidate.json")
    if not in_file.exists():
        print("未找到字段候选，请先运行 demo_table_to_dict.py")
        return
    pages = json.loads(in_file.read_text(encoding='utf-8'))

    # 生成消息定义
    msg = tables_to_message(pages, label="JX.Y", title="Auto Generated From PDF")

    # 导出
    out_dir = Path("message_output")
    out_dir.mkdir(exist_ok=True)
    json_file = out_dir / "message.json"
    xml_file = out_dir / "message.xml"
    json_file.write_text(msg.to_json(), encoding='utf-8')
    xml_file.write_text(msg.to_xml(), encoding='utf-8')

    # 简易覆盖率校验
    coverage = simple_validate_coverage(msg.fields or [])
    cov_file = out_dir / "coverage.json"
    cov_file.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding='utf-8')

    print("已生成:")
    print("-", json_file)
    print("-", xml_file)
    print("-", cov_file)


if __name__ == "__main__":
    main()


