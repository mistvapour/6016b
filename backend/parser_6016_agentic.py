#!/usr/bin/env python3
"""
MIL-STD-6016B Agentic Workflow：带自修复的 6016 消息解析。

流程：Parser(LLM) -> Validator(BSC + Note 核对) -> Refiner(错误日志 + 重试)，最多 3 次。
"""
from __future__ import annotations

import json
import os
import re
from typing import Literal

from pydantic import ValidationError

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
# 常量与提示词
# ---------------------------------------------------------------------------

MAX_ATTEMPTS = 3
SCHEMA_JSON_EXAMPLE = """
{
  "fields": [
    {
      "bit": { "start_bit": 0, "end_bit": 7, "bit_length": 8 },
      "semantic": {
        "field_name": "Example",
        "range": "0-255",
        "resolution": "1",
        "unit": "count"
      },
      "constraint": null
    }
  ]
}
"""

SYSTEM_PROMPT = """你是一个 MIL-STD-6016B 战术数据链消息解析专家。根据从 6016B PDF 提取的原始文本（含表格和 Notes），输出符合下述 JSON 结构的消息定义。

要求：
1. 每个字段必须包含 bit（start_bit, end_bit, bit_length）、semantic（field_name, range, resolution, unit，可选 lookup_table）、constraint（可选，condition 字符串）。
2. bit_length 必须等于 end_bit - start_bit + 1；位段从 0 开始连续无重叠无空隙。
3. 文本中的 "Note N" 若描述条件逻辑（如 "If ... then ..."），须在对应字段的 constraint.condition 中体现。
4. 只输出一个合法 JSON 对象，不要 markdown 代码块包裹，不要多余解释。"""

USER_PROMPT_TEMPLATE = """请将以下 6016B 原始文本解析为消息定义 JSON。预期总位长为 {total_bits} 位。

--- 原始文本 ---
{raw_text}
--- 结束 ---

输出一个 JSON，形如：{schema_example}"""

REFINER_USER_PROMPT_TEMPLATE = """请根据下面的错误日志，对之前的解析结果进行针对性修复。仍只输出一个合法 JSON，不要 markdown 包裹。

--- 原始文本 ---
{raw_text}
--- 结束 ---

--- 上一轮解析结果（可能有误）---
{previous_json}
--- 结束 ---

--- 错误日志 ---
{error_log}
--- 结束 ---

预期总位长：{total_bits} 位。请修正上述问题后重新输出完整 JSON。"""


# ---------------------------------------------------------------------------
# Note 提取与核对
# ---------------------------------------------------------------------------

def extract_notes_from_text(raw_text: str) -> list[tuple[str, str]]:
    """
    从原始文本中提取 "Note N" 及其内容。
    返回 [(note_label, note_content), ...]，如 [("Note 1", "If A=1 then ..."), ...]。
    """
    if not raw_text or not raw_text.strip():
        return []
    notes: list[tuple[str, str]] = []
    # 匹配 "Note 1", "Note 2", "Note 1:" 等，不区分大小写
    pattern = re.compile(
        r"\bNote\s*(\d+)\s*[.:]?\s*(.*?)(?=\bNote\s*\d+\s*[.:]?|$)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(raw_text):
        num = m.group(1)
        content = (m.group(2) or "").strip()
        if content:
            notes.append((f"Note {num}", content))
    return notes


def validate_notes_captured(
    raw_text: str,
    message: MessageSchema,
) -> tuple[bool, list[str]]:
    """
    检查文本中的 Note 是否在 JSON 的 constraint.condition 中被捕捉。
    返回 (是否全部捕捉, 未捕捉的 Note 描述列表)。
    """
    notes = extract_notes_from_text(raw_text)
    if not notes:
        return True, []

    conditions: list[str] = []
    for f in message.fields:
        if f.constraint and f.constraint.condition:
            conditions.append(f.constraint.condition.strip().lower())

    missing: list[str] = []
    for label, content in notes:
        # 若 Note 内容过短或纯数字，可视为无实质条件，跳过
        content_clean = content.strip()
        if len(content_clean) < 3:
            continue
        # 取 Note 内容中的关键片段（前 50 字或整段若较短）
        key_fragment = content_clean[:50].lower() if len(content_clean) > 50 else content_clean.lower()
        # 检查是否有任意 constraint.condition 包含该片段的主要词
        words = [w for w in re.split(r"\W+", key_fragment) if len(w) > 1]
        if not words:
            continue
        found = any(
            any(w in c for w in words) for c in conditions
        )
        if not found:
            missing.append(f"未捕捉到 {label} 的条件逻辑：{content_clean[:80]}...")
    return (len(missing) == 0, missing)


# ---------------------------------------------------------------------------
# LLM 调用（OpenAI / Anthropic）
# ---------------------------------------------------------------------------

def _call_openai(user_content: str, system_content: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 OPENAI_API_KEY，无法调用 OpenAI")
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("请安装 openai: pip install openai")
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


def _call_anthropic(user_content: str, system_content: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 ANTHROPIC_API_KEY，无法调用 Anthropic")
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("请安装 anthropic: pip install anthropic")
    client = Anthropic(api_key=api_key)
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_content,
        messages=[{"role": "user", "content": user_content}],
    )
    text = resp.content[0].text if resp.content else ""
    return text.strip()


def call_llm(
    user_content: str,
    system_content: str,
    provider: Literal["openai", "anthropic"] = "openai",
) -> str:
    if provider == "openai":
        return _call_openai(user_content, system_content)
    if provider == "anthropic":
        return _call_anthropic(user_content, system_content)
    raise ValueError(f"不支持的 provider: {provider}")


# ---------------------------------------------------------------------------
# JSON 解析为 MessageSchema
# ---------------------------------------------------------------------------

def _extract_json_from_response(response: str) -> str:
    """从 LLM 回复中剥离 markdown 代码块（若有）并取 JSON 字符串。"""
    s = response.strip()
    # 去掉 ```json ... ``` 或 ``` ... ```
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", s, re.DOTALL)
    if m:
        s = m.group(1).strip()
    return s


def parse_message_schema_from_json(json_str: str) -> MessageSchema:
    """将 JSON 字符串解析为 MessageSchema，解析失败时抛出 ValueError。"""
    try:
        raw = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}") from e
    if not isinstance(raw, dict) or "fields" not in raw:
        raise ValueError("JSON 必须包含 'fields' 数组")
    try:
        return MessageSchema.model_validate(raw)
    except ValidationError as e:
        raise ValueError(f"MessageSchema 校验失败: {e}") from e


# ---------------------------------------------------------------------------
# Validator：BSC + Note 核对，生成 error_log
# ---------------------------------------------------------------------------

def validate_and_build_error_log(
    raw_text: str,
    total_bits: int,
    message: MessageSchema,
) -> tuple[bool, str]:
    """
    执行 BSC 完整性校验与 Note 条件核对；若失败则生成 error_log 字符串。
    返回 (是否通过, error_log)；通过时 error_log 为空字符串。
    """
    errors: list[str] = []

    ok_bsc, bsc_errors = message.validate_bsc_integrity(total_bits)
    if not ok_bsc:
        errors.extend(bsc_errors)

    ok_notes, note_errors = validate_notes_captured(raw_text, message)
    if not ok_notes:
        errors.extend(note_errors)

    if not errors:
        return True, ""
    return False, "；".join(errors)


# ---------------------------------------------------------------------------
# 主入口：parse_6016_message_with_self_repair
# ---------------------------------------------------------------------------

class Parse6016SelfRepairError(Exception):
    """在最大尝试次数内仍无法通过校验时抛出，需人工介入。"""
    def __init__(self, message: str, last_result: MessageSchema | None, error_log: str, attempts: int):
        self.last_result = last_result
        self.error_log = error_log
        self.attempts = attempts
        super().__init__(message)


def parse_6016_message_with_self_repair(
    raw_text: str,
    total_bits: int,
    provider: Literal["openai", "anthropic"] = "openai",
    max_attempts: int = MAX_ATTEMPTS,
) -> MessageSchema:
    """
    Agentic Workflow：Parser -> Validator -> Refiner（最多 max_attempts 次）。

    - Parser：调用 LLM 将原始文本转为 MessageSchema JSON。
    - Validator：validate_bsc_integrity(total_bits) + 核对文本中 Note 是否被 constraint 捕捉。
    - Refiner：若失败则生成 error_log，将 原始文本 + 上一轮结果 + error_log 再次发给 LLM 修复。

    若超过 max_attempts 仍不通过，抛出 Parse6016SelfRepairError，供人工介入。
    """
    if max_attempts < 1:
        raise ValueError("max_attempts 至少为 1")

    last_result: MessageSchema | None = None
    last_json_str = ""
    error_log = ""

    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            user_content = USER_PROMPT_TEMPLATE.format(
                total_bits=total_bits,
                raw_text=raw_text,
                schema_example=SCHEMA_JSON_EXAMPLE.strip(),
            )
        else:
            user_content = REFINER_USER_PROMPT_TEMPLATE.format(
                raw_text=raw_text,
                previous_json=last_json_str,
                error_log=error_log,
                total_bits=total_bits,
            )

        try:
            response = call_llm(user_content, SYSTEM_PROMPT, provider=provider)
            json_str = _extract_json_from_response(response)
            last_json_str = json_str  # 供下一轮 Refiner 使用（含解析失败时）
            message = parse_message_schema_from_json(json_str)
            last_result = message
        except (ValueError, RuntimeError) as e:
            error_log = f"第 {attempt} 轮解析或校验异常: {e}"
            if attempt == max_attempts:
                raise Parse6016SelfRepairError(
                    f"经 {max_attempts} 次尝试后仍失败：{error_log}",
                    last_result=last_result,
                    error_log=error_log,
                    attempts=attempt,
                ) from e
            continue

        ok, error_log = validate_and_build_error_log(raw_text, total_bits, message)
        if ok:
            return message

        if attempt == max_attempts:
            raise Parse6016SelfRepairError(
                f"经 {max_attempts} 次尝试后校验仍未通过。最后错误：{error_log}",
                last_result=last_result,
                error_log=error_log,
                attempts=attempt,
            )

    # 理论上不会走到
    raise Parse6016SelfRepairError(
        "解析流程异常结束",
        last_result=last_result,
        error_log=error_log or "未知",
        attempts=max_attempts,
    )


__all__ = [
    "parse_6016_message_with_self_repair",
    "Parse6016SelfRepairError",
    "extract_notes_from_text",
    "validate_notes_captured",
    "validate_and_build_error_log",
    "call_llm",
]
