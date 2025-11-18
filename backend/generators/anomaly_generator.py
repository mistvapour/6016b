#!/usr/bin/env python3
"""
异常结构消息生成器
支持生成带有边界特征或结构异常的消息样本，用于协议鲁棒性评估与错误处理测试
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Any, List, Optional
import random
import copy

from backend.schema.message_definition import MessageDefinition, MessageField


class AnomalyStrategy(str, Enum):
    """异常注入策略"""
    MISSING_FIELD = "missing_field"          # 字段缺失
    TYPE_MISMATCH = "type_mismatch"          # 类型错误
    OUT_OF_BOUNDS = "out_of_bounds"          # 越界值
    ENCODING_ERROR = "encoding_error"        # 编码错误
    NESTED_LEVEL_ERROR = "nested_level"      # 嵌套层级错误
    BIT_OVERFLOW = "bit_overflow"            # 位段溢出
    RANDOM = "random"                        # 随机异常


class AnomalyMessageGenerator:
    """异常消息生成器"""
    
    def __init__(self, strategy: AnomalyStrategy = AnomalyStrategy.RANDOM):
        """
        初始化异常生成器
        
        Args:
            strategy: 异常注入策略
        """
        self.strategy = strategy
    
    def inject_anomaly(self, message_def: MessageDefinition, 
                      instance: Dict[str, Any],
                      target_field: Optional[str] = None) -> Dict[str, Any]:
        """
        注入异常到消息实例
        
        Args:
            message_def: 消息定义
            instance: 原始消息实例
            target_field: 目标字段名（None表示随机选择）
        
        Returns:
            包含异常的消息实例
        """
        # 深拷贝避免修改原始实例
        anomalous_instance = copy.deepcopy(instance)
        
        if self.strategy == AnomalyStrategy.MISSING_FIELD:
            return self._inject_missing_fields(message_def, anomalous_instance, target_field)
        elif self.strategy == AnomalyStrategy.TYPE_MISMATCH:
            return self._inject_type_mismatch(message_def, anomalous_instance, target_field)
        elif self.strategy == AnomalyStrategy.OUT_OF_BOUNDS:
            return self._inject_out_of_bounds(message_def, anomalous_instance, target_field)
        elif self.strategy == AnomalyStrategy.ENCODING_ERROR:
            return self._inject_encoding_error(message_def, anomalous_instance, target_field)
        elif self.strategy == AnomalyStrategy.NESTED_LEVEL_ERROR:
            return self._inject_nested_level_error(message_def, anomalous_instance)
        elif self.strategy == AnomalyStrategy.BIT_OVERFLOW:
            return self._inject_bit_overflow(message_def, anomalous_instance, target_field)
        else:  # RANDOM
            return self._inject_random_anomaly(message_def, anomalous_instance)
    
    def _inject_missing_fields(self, message_def: MessageDefinition, 
                              instance: Dict[str, Any],
                              target_field: Optional[str]) -> Dict[str, Any]:
        """注入字段缺失异常"""
        if not message_def.fields:
            return instance
        
        # 选择要删除的字段
        if target_field:
            if target_field in instance:
                del instance[target_field]
        else:
            # 随机删除一个字段
            fields_to_remove = [f.name for f in message_def.fields if f.name in instance]
            if fields_to_remove:
                field_to_remove = random.choice(fields_to_remove)
                del instance[field_to_remove]
        
        return instance
    
    def _inject_type_mismatch(self, message_def: MessageDefinition, 
                             instance: Dict[str, Any],
                             target_field: Optional[str]) -> Dict[str, Any]:
        """注入类型错误异常"""
        if not message_def.fields:
            return instance
        
        # 选择目标字段
        if target_field:
            field = next((f for f in message_def.fields if f.name == target_field), None)
        else:
            # 随机选择一个字段
            available_fields = [f for f in message_def.fields if f.name in instance]
            if not available_fields:
                return instance
            field = random.choice(available_fields)
            target_field = field.name
        
        if not field:
            return instance
        
        # 根据原始类型生成错误类型
        original_value = instance[target_field]
        dtype = field.dtype.lower()
        
        if dtype in ["uint", "int", "uint8", "int8", "uint16", "int16", "uint32", "int32"]:
            # 将整数改为字符串或浮点数
            instance[target_field] = random.choice([
                "invalid_string",
                float(random.randint(1000, 9999)),
                None,
            ])
        elif dtype in ["float", "double", "float32", "float64"]:
            # 将浮点数改为字符串或整数
            instance[target_field] = random.choice([
                "invalid_float",
                random.randint(1000, 9999),
                None,
            ])
        elif dtype == "string":
            # 将字符串改为整数或字典
            instance[target_field] = random.choice([
                random.randint(1000, 9999),
                {"invalid": "dict"},
                None,
            ])
        elif dtype == "bool":
            # 将布尔值改为整数或字符串
            instance[target_field] = random.choice([
                random.randint(0, 100),
                "invalid_bool",
                None,
            ])
        
        return instance
    
    def _inject_out_of_bounds(self, message_def: MessageDefinition, 
                             instance: Dict[str, Any],
                             target_field: Optional[str]) -> Dict[str, Any]:
        """注入越界值异常"""
        if not message_def.fields:
            return instance
        
        # 选择目标字段
        if target_field:
            field = next((f for f in message_def.fields if f.name == target_field), None)
        else:
            # 选择有约束的数值字段
            numeric_fields = [
                f for f in message_def.fields 
                if f.constraint and f.name in instance and 
                (f.constraint.min_value is not None or f.constraint.max_value is not None)
            ]
            if not numeric_fields:
                return instance
            field = random.choice(numeric_fields)
            target_field = field.name
        
        if not field or not field.constraint:
            return instance
        
        # 生成越界值
        if field.constraint.min_value is not None and field.constraint.max_value is not None:
            # 随机选择小于最小值或大于最大值
            if random.choice([True, False]):
                instance[target_field] = field.constraint.min_value - random.randint(1, 1000)
            else:
                instance[target_field] = field.constraint.max_value + random.randint(1, 1000)
        elif field.constraint.min_value is not None:
            instance[target_field] = field.constraint.min_value - random.randint(1, 1000)
        elif field.constraint.max_value is not None:
            instance[target_field] = field.constraint.max_value + random.randint(1, 1000)
        
        return instance
    
    def _inject_encoding_error(self, message_def: MessageDefinition, 
                              instance: Dict[str, Any],
                              target_field: Optional[str]) -> Dict[str, Any]:
        """注入编码错误异常"""
        if not message_def.fields:
            return instance
        
        # 选择目标字段
        if target_field:
            field = next((f for f in message_def.fields if f.name == target_field), None)
        else:
            # 优先选择字符串字段
            string_fields = [f for f in message_def.fields if f.name in instance and f.dtype.lower() == "string"]
            if not string_fields:
                # 如果没有字符串字段，选择任意字段
                available_fields = [f for f in message_def.fields if f.name in instance]
                if not available_fields:
                    return instance
                field = random.choice(available_fields)
            else:
                field = random.choice(string_fields)
            target_field = field.name
        
        if not field:
            return instance
        
        # 注入编码错误
        if field.dtype.lower() == "string":
            # 注入无效UTF-8字符或超长字符串
            instance[target_field] = random.choice([
                b'\xFF\xFE\xFD'.decode('utf-8', errors='ignore'),  # 无效UTF-8
                "A" * 100000,  # 超长字符串
                "\x00\x01\x02",  # 包含控制字符
            ])
        else:
            # 对于非字符串字段，注入无效值
            instance[target_field] = None
        
        return instance
    
    def _inject_nested_level_error(self, message_def: MessageDefinition, 
                                   instance: Dict[str, Any]) -> Dict[str, Any]:
        """注入嵌套层级错误"""
        # 查找嵌套字段
        def find_nested_fields(fields: List[MessageField], path: str = "") -> List[tuple]:
            nested = []
            for field in fields:
                current_path = f"{path}.{field.name}" if path else field.name
                if field.children:
                    nested.append((current_path, field))
                    nested.extend(find_nested_fields(field.children, current_path))
            return nested
        
        nested_fields = find_nested_fields(message_def.fields or [])
        if not nested_fields:
            return instance
        
        # 随机选择一个嵌套字段进行破坏
        path, field = random.choice(nested_fields)
        field_path = path.split('.')
        
        # 破坏嵌套结构
        current = instance
        for part in field_path[:-1]:
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                return instance
        
        last_part = field_path[-1]
        if last_part in current:
            # 将嵌套结构替换为扁平值或错误结构
            current[last_part] = random.choice([
                "invalid_nested_string",
                random.randint(1000, 9999),
                None,
                [],  # 空列表
            ])
        
        return instance
    
    def _inject_bit_overflow(self, message_def: MessageDefinition, 
                             instance: Dict[str, Any],
                             target_field: Optional[str]) -> Dict[str, Any]:
        """注入位段溢出异常"""
        if not message_def.fields:
            return instance
        
        # 选择有位段的数值字段
        if target_field:
            field = next((f for f in message_def.fields if f.name == target_field and f.bits), None)
        else:
            bit_fields = [f for f in message_def.fields if f.bits and f.name in instance]
            if not bit_fields:
                return instance
            field = random.choice(bit_fields)
            target_field = field.name
        
        if not field or not field.bits:
            return instance
        
        # 计算位段最大值
        bit_length = field.bits[1] - field.bits[0] + 1
        max_value = (1 << bit_length) - 1
        
        # 注入溢出值
        instance[target_field] = max_value + random.randint(1, 1000)
        
        return instance
    
    def _inject_random_anomaly(self, message_def: MessageDefinition, 
                              instance: Dict[str, Any]) -> Dict[str, Any]:
        """注入随机异常"""
        strategies = [
            AnomalyStrategy.MISSING_FIELD,
            AnomalyStrategy.TYPE_MISMATCH,
            AnomalyStrategy.OUT_OF_BOUNDS,
            AnomalyStrategy.ENCODING_ERROR,
            AnomalyStrategy.BIT_OVERFLOW,
        ]
        
        # 随机选择策略
        strategy = random.choice(strategies)
        temp_generator = AnomalyMessageGenerator(strategy=strategy)
        return temp_generator.inject_anomaly(message_def, instance)
    
    def generate_anomaly_batch(self, message_def: MessageDefinition, 
                               instance: Dict[str, Any],
                               count: int = 10) -> List[Dict[str, Any]]:
        """
        批量生成异常消息实例
        
        Args:
            message_def: 消息定义
            instance: 原始消息实例
            count: 生成数量
        
        Returns:
            异常消息实例列表
        """
        anomalies = []
        for i in range(count):
            if self.strategy == AnomalyStrategy.RANDOM:
                # 每次使用随机策略
                anomaly = self._inject_random_anomaly(message_def, copy.deepcopy(instance))
            else:
                anomaly = self.inject_anomaly(message_def, copy.deepcopy(instance))
            anomalies.append(anomaly)
        
        return anomalies


__all__ = ["AnomalyMessageGenerator", "AnomalyStrategy"]

