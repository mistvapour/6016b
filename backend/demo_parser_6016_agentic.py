#!/usr/bin/env python3
"""
演示 parse_6016_message_with_self_repair：若未设置 LLM API Key 则仅运行 Validator 与 Note 提取。
"""
from __future__ import annotations

import os
import json

# 从 backend 根运行：python demo_parser_6016_agentic.py 或 python -m parser_6016_agentic 的兄弟
try:
    from parser_6016_agentic import (
        parse_6016_message_with_self_repair,
        Parse6016SelfRepairError,
        extract_notes_from_text,
        validate_and_build_error_log,
    )
except ImportError:
    from backend.parser_6016_agentic import (
        parse_6016_message_with_self_repair,
        Parse6016SelfRepairError,
        extract_notes_from_text,
        validate_and_build_error_log,
    )

try:
    from schema.bsc_integrity_model import MessageSchema, FieldSchema, BitSchema, SemanticSchema, ConstraintSchema
except ImportError:
    from backend.schema.bsc_integrity_model import MessageSchema, FieldSchema, BitSchema, SemanticSchema, ConstraintSchema


SAMPLE_RAW_TEXT = """
Message J12.0  Example (24 bits)

Bits    Mnemonic    Resolution    Unit    Range
0-7     Field_A     1             count   0-255
8-15    Field_B     0.1           deg     0-360
16-23   Field_C     1             m       0-65535

Note 1: If Field_A == 0, then Field_B and Field_C are reserved.
Note 2: When Field_A > 0, Field_B indicates bearing in degrees.
"""


def run_validator_only():
    """未配置 API Key 时：仅演示 Validator（BSC + Note 核对）与 error_log 生成。"""
    print("未检测到 OPENAI_API_KEY / ANTHROPIC_API_KEY，仅运行 Validator 演示。\n")

    # 构造一个故意有误的 MessageSchema：位长和=24 但少 3 位（只 21）、且未体现 Note 1
    msg = MessageSchema(fields=[
        FieldSchema(
            bit=BitSchema(start_bit=0, end_bit=6, bit_length=7),
            semantic=SemanticSchema(field_name="Field_A", range="0-255", resolution="1", unit="count"),
        ),
        FieldSchema(
            bit=BitSchema(start_bit=7, end_bit=14, bit_length=8),
            semantic=SemanticSchema(field_name="Field_B", range="0-360", resolution="0.1", unit="deg"),
        ),
        FieldSchema(
            bit=BitSchema(start_bit=15, end_bit=22, bit_length=8),
            semantic=SemanticSchema(field_name="Field_C", range="0-65535", resolution="1", unit="m"),
        ),
    ])
    total_bits = 24
    ok, error_log = validate_and_build_error_log(SAMPLE_RAW_TEXT, total_bits, msg)
    print("validate_and_build_error_log 结果:", ok)
    print("error_log:", error_log or "(无)")
    print()

    notes = extract_notes_from_text(SAMPLE_RAW_TEXT)
    print("提取的 Note 数量:", len(notes))
    for label, content in notes:
        print(f"  {label}: {content[:60]}...")
    print()

    # 修正后：24 位连续，并为 Field_B 加上 Note 1 相关 condition
    msg_fixed = MessageSchema(fields=[
        FieldSchema(
            bit=BitSchema(start_bit=0, end_bit=7, bit_length=8),
            semantic=SemanticSchema(field_name="Field_A", range="0-255", resolution="1", unit="count"),
        ),
        FieldSchema(
            bit=BitSchema(start_bit=8, end_bit=15, bit_length=8),
            semantic=SemanticSchema(field_name="Field_B", range="0-360", resolution="0.1", unit="deg"),
            constraint=ConstraintSchema(
                condition="If Field_A == 0, then Field_B and Field_C are reserved; when Field_A > 0, Field_B indicates bearing in degrees.",
            ),
        ),
        FieldSchema(
            bit=BitSchema(start_bit=16, end_bit=23, bit_length=8),
            semantic=SemanticSchema(field_name="Field_C", range="0-65535", resolution="1", unit="m"),
        ),
    ])
    ok2, error_log2 = validate_and_build_error_log(SAMPLE_RAW_TEXT, total_bits, msg_fixed)
    print("修正后 validate_and_build_error_log:", ok2, "error_log:", error_log2 or "(无)")


def run_full_workflow():
    """已配置 API Key 时：调用 parse_6016_message_with_self_repair。"""
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"
    print(f"使用 provider: {provider}，调用 parse_6016_message_with_self_repair...\n")
    try:
        msg = parse_6016_message_with_self_repair(SAMPLE_RAW_TEXT, total_bits=24, provider=provider)
        print("解析成功。MessageSchema (JSON):")
        print(json.dumps(msg.model_dump(), ensure_ascii=False, indent=2))
    except Parse6016SelfRepairError as e:
        print("需人工介入:", e)
        print("最后错误:", e.error_log)
        print("尝试次数:", e.attempts)
        if e.last_result:
            print("上一轮结果 (JSON):", e.last_result.model_dump())


if __name__ == "__main__":
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        run_full_workflow()
    else:
        run_validator_only()
