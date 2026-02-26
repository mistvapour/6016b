#!/usr/bin/env python3
"""
消息实例自动生成器
支持根据字段类型与约束条件自动填充默认值、随机值、边界值与异常值
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Any, List, Optional
import random
import datetime
from dataclasses import asdict

try:
    from schema.message_definition import MessageDefinition, MessageField, FieldConstraint
except ImportError:
    from backend.schema.message_definition import MessageDefinition, MessageField, FieldConstraint


class GenerationMode(str, Enum):
    """生成模式"""
    DEFAULT = "default"      # 默认值
    RANDOM = "random"         # 随机值
    BOUNDARY = "boundary"     # 边界值
    ANOMALY = "anomaly"       # 异常值


class MessageInstanceGenerator:
    """消息实例生成器"""
    
    def __init__(self, mode: GenerationMode = GenerationMode.DEFAULT):
        """
        初始化生成器
        
        Args:
            mode: 生成模式（default/random/boundary/anomaly）
        """
        self.mode = mode
        self.random_seed = None
        
    def set_random_seed(self, seed: int):
        """设置随机种子"""
        self.random_seed = seed
        random.seed(seed)
    
    def generate(self, message_def: MessageDefinition, 
                 fill_header: bool = True,
                 custom_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成消息实例
        
        Args:
            message_def: 消息定义
            fill_header: 是否自动填充消息头字段
            custom_values: 自定义字段值（覆盖自动生成）
        
        Returns:
            消息实例字典
        """
        instance = {}
        
        # 填充消息头
        if fill_header:
            instance.update(self._generate_header(message_def))
        
        # 生成字段值
        if message_def.fields:
            for field in message_def.fields:
                field_value = self._generate_field_value(field)
                instance[field.name] = field_value
        
        # 应用自定义值
        if custom_values:
            instance.update(custom_values)
        
        return instance
    
    def _generate_header(self, message_def: MessageDefinition) -> Dict[str, Any]:
        """生成消息头字段"""
        header = {
            "message_type": message_def.label,
            "message_title": message_def.title,
            "version": message_def.version,
            "timestamp": datetime.datetime.now().isoformat(),
            "sequence_number": random.randint(1, 65535) if self.mode != GenerationMode.DEFAULT else 1,
        }
        return header
    
    def _generate_field_value(self, field: MessageField) -> Any:
        """生成单个字段值"""
        # 处理嵌套字段
        if field.children:
            return self._generate_nested_field(field)
        
        # 根据生成模式生成值
        if self.mode == GenerationMode.DEFAULT:
            return self._generate_default_value(field)
        elif self.mode == GenerationMode.RANDOM:
            return self._generate_random_value(field)
        elif self.mode == GenerationMode.BOUNDARY:
            return self._generate_boundary_value(field)
        elif self.mode == GenerationMode.ANOMALY:
            return self._generate_anomaly_value(field)
        else:
            return self._generate_default_value(field)
    
    def _generate_nested_field(self, field: MessageField) -> Dict[str, Any]:
        """生成嵌套字段"""
        nested = {}
        if field.children:
            for child in field.children:
                nested[child.name] = self._generate_field_value(child)
        return nested
    
    def _generate_default_value(self, field: MessageField) -> Any:
        """生成默认值"""
        constraint = field.constraint
        
        # 枚举类型：选择第一个值
        if constraint and constraint.enum:
            return constraint.enum[0]
        
        # 根据数据类型生成默认值
        dtype = field.dtype.lower()
        
        if dtype in ["uint", "int", "uint8", "uint16", "uint32", "int8", "int16", "int32"]:
            if constraint and constraint.min_value is not None:
                return int(constraint.min_value)
            return 0
        
        elif dtype in ["float", "double", "float32", "float64"]:
            if constraint and constraint.min_value is not None:
                return float(constraint.min_value)
            return 0.0
        
        elif dtype == "enum":
            if constraint and constraint.enum:
                return constraint.enum[0]
            return "UNKNOWN"
        
        elif dtype == "bool" or dtype == "boolean":
            return False
        
        elif dtype == "string":
            # 根据字段名生成合理的默认字符串
            name_lower = field.name.lower()
            if "id" in name_lower or "identifier" in name_lower:
                return "ID00001"
            elif "status" in name_lower:
                return "ACTIVE"
            elif "mode" in name_lower:
                return "NORMAL"
            else:
                return ""
        
        else:
            return ""
    
    def _generate_random_value(self, field: MessageField) -> Any:
        """生成随机值"""
        constraint = field.constraint
        
        # 枚举类型：随机选择一个值
        if constraint and constraint.enum:
            return random.choice(constraint.enum)
        
        # 根据数据类型生成随机值
        dtype = field.dtype.lower()
        
        if dtype in ["uint", "int", "uint8", "uint16", "uint32", "int8", "int16", "int32"]:
            min_val = int(constraint.min_value) if constraint and constraint.min_value is not None else 0
            max_val = int(constraint.max_value) if constraint and constraint.max_value is not None else 65535
            
            # 根据位段长度推断最大值
            if field.bits:
                bit_length = field.bits[1] - field.bits[0] + 1
                max_val = min(max_val, (1 << bit_length) - 1)
            
            return random.randint(min_val, max_val)
        
        elif dtype in ["float", "double", "float32", "float64"]:
            min_val = float(constraint.min_value) if constraint and constraint.min_value is not None else 0.0
            max_val = float(constraint.max_value) if constraint and constraint.max_value is not None else 1000.0
            return random.uniform(min_val, max_val)
        
        elif dtype == "enum":
            if constraint and constraint.enum:
                return random.choice(constraint.enum)
            return "UNKNOWN"
        
        elif dtype == "bool" or dtype == "boolean":
            return random.choice([True, False])
        
        elif dtype == "string":
            # 生成随机字符串
            name_lower = field.name.lower()
            if "id" in name_lower or "identifier" in name_lower:
                return f"ID{random.randint(10000, 99999)}"
            elif "status" in name_lower:
                statuses = ["ACTIVE", "INACTIVE", "STANDBY", "ERROR"]
                return random.choice(statuses)
            elif "mode" in name_lower:
                modes = ["NORMAL", "EMERGENCY", "TEST", "MAINTENANCE"]
                return random.choice(modes)
            else:
                length = random.randint(5, 20)
                return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=length))
        
        else:
            return ""
    
    def _generate_boundary_value(self, field: MessageField) -> Any:
        """生成边界值"""
        constraint = field.constraint
        
        # 枚举类型：返回第一个或最后一个
        if constraint and constraint.enum:
            # 随机选择第一个或最后一个
            return random.choice([constraint.enum[0], constraint.enum[-1]])
        
        # 根据数据类型生成边界值
        dtype = field.dtype.lower()
        
        if dtype in ["uint", "int", "uint8", "uint16", "uint32", "int8", "int16", "int32"]:
            min_val = int(constraint.min_value) if constraint and constraint.min_value is not None else 0
            max_val = int(constraint.max_value) if constraint and constraint.max_value is not None else 65535
            
            # 根据位段长度推断最大值
            if field.bits:
                bit_length = field.bits[1] - field.bits[0] + 1
                max_val = min(max_val, (1 << bit_length) - 1)
            
            # 随机选择最小值、最大值、最小值+1、最大值-1
            boundary_options = [min_val, max_val]
            if max_val > min_val:
                if min_val + 1 <= max_val:
                    boundary_options.append(min_val + 1)
                if max_val - 1 >= min_val:
                    boundary_options.append(max_val - 1)
            
            return random.choice(boundary_options)
        
        elif dtype in ["float", "double", "float32", "float64"]:
            min_val = float(constraint.min_value) if constraint and constraint.min_value is not None else 0.0
            max_val = float(constraint.max_value) if constraint and constraint.max_value is not None else 1000.0
            
            # 随机选择最小值、最大值、最小值+epsilon、最大值-epsilon
            epsilon = (max_val - min_val) * 0.001 if max_val > min_val else 0.001
            boundary_options = [min_val, max_val]
            if max_val > min_val:
                boundary_options.extend([min_val + epsilon, max_val - epsilon])
            
            return random.choice(boundary_options)
        
        elif dtype == "bool" or dtype == "boolean":
            return random.choice([True, False])
        
        elif dtype == "string":
            # 返回空字符串或最大长度字符串
            return random.choice(["", "A" * 100])
        
        else:
            return self._generate_default_value(field)
    
    def _generate_anomaly_value(self, field: MessageField) -> Any:
        """生成异常值（用于测试错误处理）"""
        constraint = field.constraint
        
        # 根据数据类型生成异常值
        dtype = field.dtype.lower()
        
        if dtype in ["uint", "int", "uint8", "uint16", "uint32", "int8", "int16", "int32"]:
            min_val = int(constraint.min_value) if constraint and constraint.min_value is not None else 0
            max_val = int(constraint.max_value) if constraint and constraint.max_value is not None else 65535
            
            # 生成超出范围的值
            anomaly_options = [
                min_val - 1,        # 小于最小值
                max_val + 1,        # 大于最大值
                -1,                 # 负数（对于uint类型）
            ]
            
            # 根据位段长度推断最大值
            if field.bits:
                bit_length = field.bits[1] - field.bits[0] + 1
                max_possible = (1 << bit_length) - 1
                anomaly_options.append(max_possible + 1)
            
            return random.choice(anomaly_options)
        
        elif dtype in ["float", "double", "float32", "float64"]:
            min_val = float(constraint.min_value) if constraint and constraint.min_value is not None else 0.0
            max_val = float(constraint.max_value) if constraint and constraint.max_value is not None else 1000.0
            
            # 生成超出范围或特殊值
            anomaly_options = [
                min_val - 1.0,      # 小于最小值
                max_val + 1.0,      # 大于最大值
                float('inf'),       # 无穷大
                float('-inf'),      # 负无穷
                float('nan'),       # NaN
            ]
            
            return random.choice(anomaly_options)
        
        elif dtype == "enum":
            # 返回不在枚举列表中的值
            if constraint and constraint.enum:
                return "INVALID_ENUM_VALUE"
            return "UNKNOWN"
        
        elif dtype == "string":
            # 返回超长字符串或特殊字符
            anomaly_options = [
                "A" * 10000,        # 超长字符串
                "",                 # 空字符串（如果required=True）
                "NULL\x00\x01",     # 包含特殊字符
            ]
            return random.choice(anomaly_options)
        
        else:
            # 类型错误：返回错误类型
            return None  # 对于期望非None的字段
    
    def generate_batch(self, message_def: MessageDefinition, 
                       count: int = 10,
                       fill_header: bool = True) -> List[Dict[str, Any]]:
        """
        批量生成消息实例
        
        Args:
            message_def: 消息定义
            count: 生成数量
            fill_header: 是否自动填充消息头字段
        
        Returns:
            消息实例列表
        """
        instances = []
        for i in range(count):
            # 对于随机模式，每次生成不同的值
            if self.mode == GenerationMode.RANDOM:
                random.seed(None)  # 重置随机种子
            
            instance = self.generate(message_def, fill_header=fill_header)
            instances.append(instance)
        
        return instances


__all__ = ["MessageInstanceGenerator", "GenerationMode"]

