#!/usr/bin/env python3
"""
消息生成器模块
"""
try:
    from backend.generators.message_instance_generator import MessageInstanceGenerator, GenerationMode
except ImportError:
    from generators.message_instance_generator import MessageInstanceGenerator, GenerationMode

try:
    from backend.generators.binary_instance_generator import (
        generate_binary_instance,
        check_instance_logic_compliance,
    )
except ImportError:
    from generators.binary_instance_generator import (
        generate_binary_instance,
        check_instance_logic_compliance,
    )

__all__ = [
    "MessageInstanceGenerator",
    "GenerationMode",
    "generate_binary_instance",
    "check_instance_logic_compliance",
]

