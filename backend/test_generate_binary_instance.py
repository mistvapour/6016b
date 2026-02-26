#!/usr/bin/env python3
"""
6016B 消息实例生成器批量测试与量化评估。

- 批量生成 100 个实例，统计：
  - 物理闭合合格率：生成的报文长度是否永远等于预期长度。
  - 逻辑合规率：是否严格遵守 Note 中的 if-else 约束。
- 日志配置便于论文中截取「自修复过程」等实验证据。
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime

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

try:
    from generators.binary_instance_generator import (
        generate_binary_instance,
        check_instance_logic_compliance,
    )
except ImportError:
    from backend.generators.binary_instance_generator import (
        generate_binary_instance,
        check_instance_logic_compliance,
    )


# ---------------------------------------------------------------------------
# 论文用日志配置
# ---------------------------------------------------------------------------

LOG_TAG_PHYSICAL = "PhysicalClosure"
LOG_TAG_LOGIC = "LogicCompliance"
LOG_TAG_BATCH = "BatchGen"
LOG_TAG_STATS = "Stats"


def setup_logging(
    log_dir: str = "logs",
    log_file_prefix: str = "bsc_binary_instance",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> str:
    """
    配置日志：控制台 + 按日期命名的文件，便于论文截取自修复过程证据。
    返回实际写入的日志文件路径。
    """
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{log_file_prefix}_{ts}.log")
    log_path = os.path.abspath(log_file)

    root = logging.getLogger()
    root.setLevel(min(console_level, file_level))
    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(console_level)
    console.setFormatter(fmt)
    root.addHandler(console)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    # 生成器模块使用 DEBUG 以便论文截取约束决策
    logging.getLogger("bsc.binary_instance_generator").setLevel(logging.DEBUG)

    return log_path


# ---------------------------------------------------------------------------
# 测试用 MessageSchema（含条件约束）
# ---------------------------------------------------------------------------

def make_sample_schema() -> tuple[MessageSchema, int]:
    """
    返回一个带 condition 的 MessageSchema 及对应 total_bits。
    Field_A 无约束；Field_B 有 condition: Field_A > 0 时才有效。
    """
    total_bits = 24
    schema = MessageSchema(
        fields=[
            FieldSchema(
                bit=BitSchema(start_bit=0, end_bit=7, bit_length=8),
                semantic=SemanticSchema(
                    field_name="Field_A",
                    range="0-255",
                    resolution="1",
                    unit="count",
                ),
            ),
            FieldSchema(
                bit=BitSchema(start_bit=8, end_bit=15, bit_length=8),
                semantic=SemanticSchema(
                    field_name="Field_B",
                    range="0-360",
                    resolution="0.1",
                    unit="deg",
                ),
                constraint=ConstraintSchema(
                    condition="If Field_A > 0, then this field exists",
                ),
            ),
            FieldSchema(
                bit=BitSchema(start_bit=16, end_bit=23, bit_length=8),
                semantic=SemanticSchema(
                    field_name="Field_C",
                    range="0-255",
                    resolution="1",
                    unit="m",
                ),
            ),
        ]
    )
    return schema, total_bits


# ---------------------------------------------------------------------------
# 批量生成与统计
# ---------------------------------------------------------------------------

def run_batch_test(
    schema: MessageSchema,
    total_bits: int,
    count: int = 100,
    seed: int | None = None,
    collect_samples: int = 0,
) -> tuple[int, int, int, list[str], list[str], list[dict]]:
    """
    批量生成 count 个实例，统计物理闭合合格数与逻辑合规数。
    collect_samples > 0 时收集前 N 条样例（用于导出）。
    返回 (物理闭合合格数, 逻辑合规数, 总数, 物理不合格描述, 逻辑不合格描述, 样例列表)。
    """
    logger = logging.getLogger("bsc.test_binary_instance")
    logger.info("[%s] 开始批量生成，count=%d, total_bits=%d", LOG_TAG_BATCH, count, total_bits)

    physical_fail_indices: list[str] = []
    logic_fail_messages: list[str] = []
    physical_ok = 0
    logic_ok = 0
    samples: list[dict] = []

    rng = __import__("random").Random(seed)
    for i in range(count):
        field_values, binary_str, hex_str = generate_binary_instance(schema, total_bits, rng=rng)
        if collect_samples > 0 and len(samples) < collect_samples:
            samples.append({
                "index": i + 1,
                "field_values": field_values,
                "binary": binary_str,
                "hex": hex_str,
                "bit_length": len(binary_str),
            })

        # 物理闭合：报文长度是否等于预期
        if len(binary_str) == total_bits:
            physical_ok += 1
            logger.debug("[%s] 实例 %d 位长合格: %d", LOG_TAG_PHYSICAL, i + 1, len(binary_str))
        else:
            physical_fail_indices.append(
                f"实例{i+1}: 位长={len(binary_str)} 预期={total_bits}"
            )
            logger.warning(
                "[%s] 实例 %d 位长不合格: 实际=%d 预期=%d",
                LOG_TAG_PHYSICAL,
                i + 1,
                len(binary_str),
                total_bits,
            )

        # 逻辑合规：是否严格遵守 condition
        ok_logic, logic_errors = check_instance_logic_compliance(schema, field_values)
        if ok_logic:
            logic_ok += 1
            logger.debug("[%s] 实例 %d 逻辑合规", LOG_TAG_LOGIC, i + 1)
        else:
            logic_fail_messages.extend(logic_errors)
            logger.warning("[%s] 实例 %d 逻辑不合规: %s", LOG_TAG_LOGIC, i + 1, "; ".join(logic_errors))

    logger.info(
        "[%s] 批量结束: 物理闭合合格=%d/%d 逻辑合规=%d/%d",
        LOG_TAG_STATS,
        physical_ok,
        count,
        logic_ok,
        count,
    )
    return (physical_ok, logic_ok, count, physical_fail_indices, logic_fail_messages, samples)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="6016B 消息实例生成器批量测试与量化评估")
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=100,
        help="生成实例数量（默认 100）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机种子（可选）",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="日志目录（默认 logs）",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="仅输出统计行，减少控制台日志",
    )
    parser.add_argument(
        "--export-samples",
        type=int,
        default=5,
        metavar="N",
        help="导出前 N 条样例到 JSON 文件（0=不导出，默认 5）",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="logs",
        help="样例结果与日志的输出目录（默认 logs）",
    )
    args = parser.parse_args()

    out_dir = args.out_dir or args.log_dir
    log_path = setup_logging(
        log_dir=out_dir,
        log_file_prefix="bsc_binary_instance",
        console_level=logging.DEBUG if not args.quiet else logging.WARNING,
        file_level=logging.DEBUG,
    )

    logger = logging.getLogger("bsc.test_binary_instance")
    logger.info("[BSC-GEN][SelfRepair] 6016B 消息实例生成器批量测试启动；日志文件: %s", log_path)

    schema, total_bits = make_sample_schema()
    physical_ok, logic_ok, count, physical_fails, logic_fails, samples = run_batch_test(
        schema, total_bits, count=args.count, seed=args.seed, collect_samples=args.export_samples
    )

    # 导出样例结果到 JSON，便于查看
    sample_path: str | None = None
    if samples:
        import json
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        sample_file = os.path.join(out_dir, f"bsc_sample_instances_{ts}.json")
        sample_path = os.path.abspath(sample_file)
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(
                {"total_bits": total_bits, "count": len(samples), "samples": samples},
                f,
                ensure_ascii=False,
                indent=2,
            )
        logger.info("[BSC-GEN][Export] 样例已导出: %s", sample_path)

    # 量化评估输出
    physical_rate = (physical_ok / count * 100) if count else 0
    logic_rate = (logic_ok / count * 100) if count else 0

    print()
    print("========== 量化评估结果 ==========")
    print(f"  物理闭合合格率: {physical_ok}/{count} = {physical_rate:.1f}%")
    print(f"  逻辑合规率:     {logic_ok}/{count} = {logic_rate:.1f}%")
    if physical_fails:
        print(f"  物理不合格:     {len(physical_fails)} 条")
        for s in physical_fails[:5]:
            print(f"    - {s}")
        if len(physical_fails) > 5:
            print(f"    ... 共 {len(physical_fails)} 条")
    if logic_fails:
        print(f"  逻辑不合格:     {len(logic_fails)} 条")
        for s in logic_fails[:5]:
            print(f"    - {s}")
        if len(logic_fails) > 5:
            print(f"    ... 共 {len(logic_fails)} 条")
    print(f"  详细日志文件:   {log_path}")
    if sample_path:
        print(f"  样例结果文件:   {sample_path}")
    print("==================================")


if __name__ == "__main__":
    main()
