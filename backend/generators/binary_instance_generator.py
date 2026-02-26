#!/usr/bin/env python3
"""
6016B 消息二进制实例生成器（基于 BSC MessageSchema）。

根据 MessageSchema 生成符合 range/resolution 的字段值，遵守 condition 约束，
并按位序拼接为二进制串与十六进制报文。便于论文实验与自修复过程日志截取。
"""
from __future__ import annotations

import logging
import random
import re
from typing import Any, Optional

try:
    from schema.bsc_integrity_model import (
        MessageSchema,
        FieldSchema,
        BitSchema,
        SemanticSchema,
        ConstraintSchema,
    )
except ImportError:
    from backend.schema.bsc_integrity_model import (
        MessageSchema,
        FieldSchema,
        BitSchema,
        SemanticSchema,
        ConstraintSchema,
    )


# ---------------------------------------------------------------------------
# 日志（便于论文截取）
# ---------------------------------------------------------------------------

logger = logging.getLogger("bsc.binary_instance_generator")


def _log(level: int, tag: str, msg: str, *args: Any, **kwargs: Any) -> None:
    """统一带标签的日志，便于论文中截取「自修复过程」等证据。"""
    full_msg = f"[BSC-GEN][{tag}] {msg}"
    logger.log(level, full_msg, *args, **kwargs)


# ---------------------------------------------------------------------------
# range / resolution 解析
# ---------------------------------------------------------------------------

def parse_range(range_str: str, bit_length: int) -> tuple[float, float]:
    """
    从 semantic.range 解析数值范围 (min_val, max_val)。
    支持 "0-255", "0..255", "0..2^N-1", "0..2^n-1" 等。
    """
    s = (range_str or "").strip()
    if not s:
        max_val = (1 << bit_length) - 1
        return (0.0, float(max_val))

    # 2^N-1 / 2^n-1
    m = re.match(r"^\s*0\s*\.\.\s*2\s*\^\s*[nN]\s*-\s*1\s*$", s, re.IGNORECASE)
    if m:
        max_val = (1 << bit_length) - 1
        return (0.0, float(max_val))

    # 单数字或 a-b / a..b
    m = re.match(r"^\s*([-\d.]+)\s*[-\.]+\s*([-\d.]+)\s*$", s)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if lo > hi:
            lo, hi = hi, lo
        return (lo, hi)

    # 单数字
    m = re.match(r"^\s*([-\d.]+)\s*$", s)
    if m:
        v = float(m.group(1))
        return (v, v)

    # 默认按位长
    max_val = (1 << bit_length) - 1
    return (0.0, float(max_val))


def parse_resolution(resolution_str: str) -> float:
    """从 semantic.resolution 解析步长（用于量化）。"""
    s = (resolution_str or "").strip()
    if not s:
        return 1.0
    try:
        return float(s)
    except ValueError:
        pass
    # 简单分数 "1/10" -> 0.1
    m = re.match(r"^\s*(\d+)\s*/\s*(\d+)\s*$", s)
    if m:
        return float(m.group(1)) / float(m.group(2))
    return 1.0


# ---------------------------------------------------------------------------
# condition 求值（安全、仅比较与逻辑）
# ---------------------------------------------------------------------------

def _normalize_field_name_for_context(name: str) -> str:
    """将字段名规范为可做 key 的形式（保留空格或转为下划线均可）。"""
    return name.strip()


def evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
    """
    根据当前已生成字段值 context (field_name -> value) 求值 condition。
    支持简单比较：如 "Field A == 1", "Field_B > 0"。
    若无法解析或求值失败，保守返回 True（生成该字段）。
    """
    if not (condition and condition.strip()):
        return True
    raw = condition.strip()
    # 尝试提取谓词：去掉 "If ... then ..." 外壳
    m = re.search(r"(?:if\s+)?(.+?)(?:\s+then\s+.+)?$", raw, re.IGNORECASE | re.DOTALL)
    if m:
        expr = m.group(1).strip().rstrip(".,;")
    else:
        expr = raw.strip().rstrip(".,;")
    if not expr:
        return True

    # 用 context 中的值替换标识符（支持 "Field A" 与 "Field_A"）
    for name, val in context.items():
        key = _normalize_field_name_for_context(name)
        # 替换整词，避免部分匹配
        pattern = re.compile(r"\b" + re.escape(key) + r"\b", re.IGNORECASE)
        safe_key = key.replace(" ", "_")
        pattern_underscore = re.compile(r"\b" + re.escape(safe_key) + r"\b", re.IGNORECASE)
        rep = str(val) if isinstance(val, (int, float)) else repr(val)
        expr = pattern.sub(rep, expr)
        expr = pattern_underscore.sub(rep, expr)

    # 仅允许数字、比较与逻辑运算符（替换后表达式应仅含安全字符）
    safe_expr = expr.replace(" and ", " ").replace(" or ", " ").replace(" not ", " ")
    allowed = re.compile(r"^[\d\s\.\+\-\*\/\(\)=!<>&|]+$")
    if not allowed.match(safe_expr):
        _log(logging.DEBUG, "Constraint", "条件无法安全求值，视为成立: %s", condition[:80])
        return True
    try:
        # 使用 restricted eval：仅比较与逻辑
        result = eval(expr)
        return bool(result)
    except Exception:
        _log(logging.DEBUG, "Constraint", "条件求值异常，视为成立: %s", condition[:80])
        return True


# ---------------------------------------------------------------------------
# 单字段值生成（符合 range + resolution）
# ---------------------------------------------------------------------------

def generate_field_value(
    semantic: SemanticSchema,
    bit_length: int,
    rng: Optional[random.Random] = None,
) -> int:
    """
    在 semantic.range 与 resolution 下生成整型编码值（用于按 bit_length 位编码）。
    """
    r = rng if rng is not None else random.Random()
    # 使用 getattr 避免与 builtin range 混淆
    range_str = getattr(semantic, "range", "") or ""
    lo, hi = parse_range(range_str, bit_length)
    res = parse_resolution(semantic.resolution)
    if res <= 0:
        res = 1.0
    # 量化到步长
    steps = (hi - lo) / res
    if steps <= 0:
        steps = 1
    step_max = max(0, min(int(steps), (1 << 20)))
    step_index = r.randint(0, step_max)
    value_float = lo + step_index * res
    # 限制在 [lo, hi] 内并适配位长
    value_float = max(lo, min(hi, value_float))
    value_int = int(round(value_float))
    max_bits = (1 << bit_length) - 1
    value_int = max(0, min(max_bits, value_int))
    return value_int


# ---------------------------------------------------------------------------
# 位序拼接：字段值 -> 二进制串 -> 十六进制
# ---------------------------------------------------------------------------

def value_to_bits(value: int, bit_length: int, msb_first: bool = True) -> list[int]:
    """将整型 value 编码为 bit_length 位列表。msb_first=True 表示高位在前。"""
    bits: list[int] = []
    for i in range(bit_length):
        if msb_first:
            bits.append((value >> (bit_length - 1 - i)) & 1)
        else:
            bits.append((value >> i) & 1)
    return bits


def bits_to_binary_string(bits: list[int]) -> str:
    """位列表转为二进制字符串（'0'/'1'）。"""
    return "".join(str(b) for b in bits)


def bits_to_hex(bits: list[int]) -> str:
    """位列表按 MSB 在前每 4 位一组转为十六进制字符串。"""
    s = bits_to_binary_string(bits)
    # 左侧补 0 到 4 的倍数
    pad = (4 - len(s) % 4) % 4
    s = "0" * pad + s
    out = []
    for i in range(0, len(s), 4):
        out.append(hex(int(s[i : i + 4], 2))[2:].upper())
    return "".join(out)


# ---------------------------------------------------------------------------
# 主入口：generate_binary_instance
# ---------------------------------------------------------------------------

def generate_binary_instance(
    schema: MessageSchema,
    total_bits: int,
    rng: Optional[random.Random] = None,
) -> tuple[dict[str, Any], str, str]:
    """
    根据 MessageSchema 生成一条符合 range/resolution 与 condition 的实例，
    并按位序拼接为二进制串与十六进制报文。

    约束处理：若某字段有 constraint.condition 且当前 context 下条件不满足，
    则该字段填 0（保留位），不生成随机值。

    返回 (field_values_dict, binary_str, hex_str)。
    """
    r = rng or random.Random()
    ordered = sorted(schema.fields, key=lambda f: f.bit.start_bit)
    context: dict[str, Any] = {}
    field_values: dict[str, Any] = {}
    bits_array: list[int] = [0] * total_bits

    for f in ordered:
        name = f.semantic.field_name
        start = f.bit.start_bit
        end = f.bit.end_bit
        n = f.bit.bit_length

        # 是否生成有效值：无约束则生成；有约束则求值
        should_generate = True
        if f.constraint and f.constraint.condition:
            should_generate = evaluate_condition(f.constraint.condition, context)
            _log(
                logging.DEBUG,
                "Constraint",
                "字段 %s condition=%s -> %s",
                name,
                f.constraint.condition[:60],
                "生成" if should_generate else "填0(保留)",
            )

        if should_generate:
            value = generate_field_value(f.semantic, n, r)
            field_values[name] = value
            context[name] = value
        else:
            value = 0
            field_values[name] = 0
            context[name] = 0

        word_bits = value_to_bits(value, n, msb_first=True)
        for i, b in enumerate(word_bits):
            bits_array[start + i] = b

    binary_str = bits_to_binary_string(bits_array)
    hex_str = bits_to_hex(bits_array)
    _log(logging.DEBUG, "Output", "生成实例 位长=%d 二进制长=%d hex=%s", total_bits, len(binary_str), hex_str[:32])
    return (field_values, binary_str, hex_str)


# ---------------------------------------------------------------------------
# 逻辑合规校验（供测试脚本统计）
# ---------------------------------------------------------------------------

def check_instance_logic_compliance(
    schema: MessageSchema,
    field_values: dict[str, Any],
) -> tuple[bool, list[str]]:
    """
    校验实例是否严格遵守 Note/condition：有 condition 的字段，
    当 condition 为假时应为 0，为真时可为任意合法值。
    返回 (是否合规, 违规描述列表)。
    """
    ordered = sorted(schema.fields, key=lambda f: f.bit.start_bit)
    errors: list[str] = []
    context_so_far: dict[str, Any] = {}

    for f in ordered:
        name = f.semantic.field_name
        val = field_values.get(name, 0)
        if f.constraint and f.constraint.condition:
            # 用「不含当前字段」的 context 求值（与生成时一致）
            cond_holds = evaluate_condition(f.constraint.condition, context_so_far)
            if not cond_holds and val != 0:
                errors.append(
                    f"字段 '{name}' 条件不满足但值非0: value={val}, condition={f.constraint.condition[:50]}"
                )
        context_so_far[name] = val

    return (len(errors) == 0, errors)


__all__ = [
    "generate_binary_instance",
    "parse_range",
    "parse_resolution",
    "evaluate_condition",
    "check_instance_logic_compliance",
    "value_to_bits",
    "bits_to_hex",
]
