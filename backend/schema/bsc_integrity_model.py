#!/usr/bin/env python3
"""
MIL-STD-6016B 战术数据链解析系统 - BSC 完整性数据模型。

BSC = Bit（位级结构）+ Semantic（语义值域）+ Constraint（逻辑约束）。
使用 Pydantic 实现位段重叠/空隙校验、语义非空校验及消息级完整性校验。
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Bit 位级结构
# ---------------------------------------------------------------------------


class BitSchema(BaseModel):
    """位级结构：start_bit, end_bit, bit_length。校验位段自洽（长度与起止一致）。"""

    start_bit: int = Field(..., ge=0, description="起始位（含）")
    end_bit: int = Field(..., ge=0, description="结束位（含）")
    bit_length: int = Field(..., gt=0, description="位长度")

    @model_validator(mode="after")
    def check_length_and_order(self) -> "BitSchema":
        if self.start_bit > self.end_bit:
            raise ValueError(
                f"start_bit ({self.start_bit}) 不得大于 end_bit ({self.end_bit})"
            )
        expected_length = self.end_bit - self.start_bit + 1
        if self.bit_length != expected_length:
            raise ValueError(
                f"bit_length ({self.bit_length}) 必须等于 end_bit - start_bit + 1 = {expected_length}"
            )
        return self


# ---------------------------------------------------------------------------
# Semantic 语义值域
# ---------------------------------------------------------------------------


class SemanticSchema(BaseModel):
    """语义值域：field_name, range, resolution, unit，可选 lookup_table。"""

    field_name: str = Field(..., min_length=1, description="字段名")
    range: str = Field(..., min_length=1, description="值域描述，如 '0-255' 或 '0..2^N-1'")
    resolution: str = Field(..., min_length=1, description="分辨率说明")
    unit: str = Field(..., min_length=1, description="单位，如 'deg', 'm'")
    lookup_table: Optional[dict[str, str | int]] = Field(
        default=None,
        description="可选查表：编码值 -> 含义",
    )


# ---------------------------------------------------------------------------
# Constraint 逻辑约束
# ---------------------------------------------------------------------------


class ConstraintSchema(BaseModel):
    """逻辑约束：condition 存储条件表达式，如 'If Field A == 1, then this field exists'。"""

    condition: str = Field(
        ...,
        min_length=1,
        description="条件逻辑字符串，如 'If Field A == 1, then this field exists'",
    )


# ---------------------------------------------------------------------------
# FieldSchema：单字段 = Bit + Semantic + 可选 Constraint
# ---------------------------------------------------------------------------


class FieldSchema(BaseModel):
    """单字段定义：位级结构 + 语义 + 可选逻辑约束。"""

    bit: BitSchema = Field(..., description="位级结构")
    semantic: SemanticSchema = Field(..., description="语义值域")
    constraint: Optional[ConstraintSchema] = Field(
        default=None,
        description="可选逻辑约束",
    )


# ---------------------------------------------------------------------------
# MessageSchema：多字段 + BSC 完整性校验
# ---------------------------------------------------------------------------


class MessageSchema(BaseModel):
    """消息模式：包含多个 FieldSchema，并提供 BSC 完整性校验。"""

    fields: list[FieldSchema] = Field(..., min_length=1, description="字段列表")

    @classmethod
    def validate_bsc_integrity(cls, message: "MessageSchema", total_bits: int) -> tuple[bool, list[str]]:
        """
        校验 BSC 完整性。

        - 所有字段的 bit_length 之和是否等于 total_bits。
        - 位段是否连续：前一个 end_bit + 1 == 后一个 start_bit（按 start_bit 排序后）。
        - 每个字段的语义属性（range, unit 等）是否非空。

        返回 (是否通过, 错误信息列表)。
        """
        errors: list[str] = []

        # 1) 语义非空
        for i, f in enumerate(message.fields):
            s = f.semantic
            if not (s.range and s.range.strip()):
                errors.append(f"字段[{i}] {s.field_name}: semantic.range 不能为空")
            if not (s.resolution and s.resolution.strip()):
                errors.append(f"字段[{i}] {s.field_name}: semantic.resolution 不能为空")
            if not (s.unit and s.unit.strip()):
                errors.append(f"字段[{i}] {s.field_name}: semantic.unit 不能为空")

        # 2) 位长度之和
        total_length = sum(f.bit.bit_length for f in message.fields)
        if total_length != total_bits:
            errors.append(
                f"位长度之和 ({total_length}) 与 total_bits ({total_bits}) 不相等"
            )

        # 3) 按 start_bit 排序后检查连续（无空隙、无重叠）
        ordered = sorted(message.fields, key=lambda x: x.bit.start_bit)
        for i in range(len(ordered) - 1):
            curr = ordered[i].bit
            next_b = ordered[i + 1].bit
            if curr.end_bit >= next_b.start_bit:
                errors.append(
                    f"位段重叠：字段 '{ordered[i].semantic.field_name}' [{curr.start_bit},{curr.end_bit}] 与 "
                    f"'{ordered[i + 1].semantic.field_name}' [{next_b.start_bit},{next_b.end_bit}]"
                )
            elif curr.end_bit + 1 != next_b.start_bit:
                errors.append(
                    f"位段存在空隙：字段 '{ordered[i].semantic.field_name}' end_bit={curr.end_bit}, "
                    f"下一字段 '{ordered[i + 1].semantic.field_name}' start_bit={next_b.start_bit}，应为 {curr.end_bit + 1}"
                )

        return (len(errors) == 0, errors)

    def validate_bsc_integrity(self, total_bits: int) -> tuple[bool, list[str]]:
        """实例方法：校验当前消息的 BSC 完整性。用法：message.validate_bsc_integrity(total_bits)。"""
        return MessageSchema.validate_bsc_integrity(self, total_bits)

__all__ = [
    "BitSchema",
    "SemanticSchema",
    "ConstraintSchema",
    "FieldSchema",
    "MessageSchema",
]
