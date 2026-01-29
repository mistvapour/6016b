#!/usr/bin/env python3
"""BSC 完整性数据模型演示：位段校验、连续性、语义非空与 validate_bsc_integrity。"""
from __future__ import annotations

try:
    from schema.bsc_integrity_model import (
        BitSchema,
        ConstraintSchema,
        FieldSchema,
        MessageSchema,
        SemanticSchema,
    )
except ImportError:
    from bsc_integrity_model import (
        BitSchema,
        ConstraintSchema,
        FieldSchema,
        MessageSchema,
        SemanticSchema,
    )


def main() -> None:
    # 1) Bit 自校验：bit_length 必须等于 end_bit - start_bit + 1
    bit_ok = BitSchema(start_bit=0, end_bit=5, bit_length=6)
    print("BitSchema 合法:", bit_ok.model_dump())

    try:
        BitSchema(start_bit=0, end_bit=5, bit_length=5)  # 应为 6
    except Exception as e:
        print("BitSchema 非法(长度不一致):", e)

    # 2) 合法消息：连续 24 位，三字段 8+8+8
    msg_ok = MessageSchema(
        fields=[
            FieldSchema(
                bit=BitSchema(start_bit=0, end_bit=7, bit_length=8),
                semantic=SemanticSchema(
                    field_name="A",
                    range="0-255",
                    resolution="1",
                    unit="count",
                ),
            ),
            FieldSchema(
                bit=BitSchema(start_bit=8, end_bit=15, bit_length=8),
                semantic=SemanticSchema(
                    field_name="B",
                    range="0-255",
                    resolution="0.1",
                    unit="deg",
                ),
            ),
            FieldSchema(
                bit=BitSchema(start_bit=16, end_bit=23, bit_length=8),
                semantic=SemanticSchema(
                    field_name="C",
                    range="0-255",
                    resolution="1",
                    unit="m",
                    lookup_table={"0": "unknown", "1": "valid"},
                ),
            ),
        ]
    )
    ok, errs = msg_ok.validate_bsc_integrity(24)
    print("合法消息 validate_bsc_integrity(24):", ok, errs if errs else "")

    # 3) 位长度之和不等于 total_bits
    ok2, errs2 = msg_ok.validate_bsc_integrity(72)
    print("total_bits=72 时:", ok2, errs2)

    # 4) 位段不连续（空隙）
    msg_gap = MessageSchema(
        fields=[
            FieldSchema(
                bit=BitSchema(start_bit=0, end_bit=7, bit_length=8),
                semantic=SemanticSchema(field_name="X", range="0-255", resolution="1", unit="x"),
            ),
            FieldSchema(
                bit=BitSchema(start_bit=10, end_bit=17, bit_length=8),  # 8-9 空隙
                semantic=SemanticSchema(field_name="Y", range="0-255", resolution="1", unit="y"),
            ),
        ]
    )
    ok3, errs3 = msg_gap.validate_bsc_integrity(16)
    print("位段空隙时:", ok3, errs3)

    # 5) 带 Constraint 的字段
    msg_const = MessageSchema(
        fields=[
            FieldSchema(
                bit=BitSchema(start_bit=0, end_bit=7, bit_length=8),
                semantic=SemanticSchema(field_name="F", range="0-1", resolution="1", unit="bool"),
                constraint=ConstraintSchema(
                    condition="If Field F == 1, then next field exists"
                ),
            ),
        ]
    )
    ok4, errs4 = msg_const.validate_bsc_integrity(8)
    print("带 Constraint 消息 validate_bsc_integrity(8):", ok4, errs4 if errs4 else "")

    print("demo 完成。")


if __name__ == "__main__":
    main()
