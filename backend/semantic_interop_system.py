#!/usr/bin/env python3
"""
语义互操作系统
实现不同消息标准间的语义一致性和消息转发功能
"""
import json
import yaml
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class MessageStandard(Enum):
    """消息标准枚举"""
    MIL_STD_6016 = "MIL-STD-6016"
    MAVLINK = "MAVLink"
    MQTT = "MQTT"
    GENERIC = "Generic"

class FieldType(Enum):
    """字段类型枚举"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    BYTES = "bytes"
    ENUM = "enum"
    TIMESTAMP = "timestamp"
    COORDINATE = "coordinate"
    IDENTIFIER = "identifier"

class SemanticCategory(Enum):
    """语义类别枚举"""
    IDENTIFICATION = "identification"  # 标识信息
    POSITION = "position"             # 位置信息
    STATUS = "status"                 # 状态信息
    COMMAND = "command"               # 命令控制
    SENSOR = "sensor"                 # 传感器数据
    COMMUNICATION = "communication"   # 通信信息
    TIMING = "timing"                 # 时间信息
    NAVIGATION = "navigation"         # 导航信息
    WEAPON = "weapon"                 # 武器信息
    METADATA = "metadata"             # 元数据

@dataclass
class SemanticField:
    """语义字段定义"""
    name: str                         # 字段名称
    semantic_id: str                  # 语义标识符
    category: SemanticCategory        # 语义类别
    field_type: FieldType            # 字段类型
    unit: Optional[str] = None       # 单位
    range_min: Optional[float] = None # 最小值
    range_max: Optional[float] = None # 最大值
    description: str = ""            # 描述
    aliases: List[str] = None        # 别名列表
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []

@dataclass
class SemanticMessage:
    """语义消息定义"""
    message_id: str                  # 消息标识符
    name: str                        # 消息名称
    standard: MessageStandard        # 所属标准
    category: SemanticCategory       # 主要语义类别
    fields: List[SemanticField]      # 字段列表
    description: str = ""            # 描述
    version: str = "1.0"            # 版本

@dataclass
class FieldMapping:
    """字段映射关系"""
    source_field: str                # 源字段
    target_field: str                # 目标字段
    transform_function: Optional[str] = None  # 转换函数名
    scaling_factor: Optional[float] = None    # 缩放因子
    offset: Optional[float] = None            # 偏移量
    enum_mapping: Optional[Dict[str, str]] = None  # 枚举映射

@dataclass
class MessageMapping:
    """消息映射关系"""
    source_message: str              # 源消息
    target_message: str              # 目标消息
    source_standard: MessageStandard # 源标准
    target_standard: MessageStandard # 目标标准
    field_mappings: List[FieldMapping] # 字段映射列表
    priority: int = 0                # 优先级
    bidirectional: bool = True       # 是否双向映射

class SemanticRegistry:
    """语义注册表"""
    
    def __init__(self):
        self.semantic_fields: Dict[str, SemanticField] = {}
        self.semantic_messages: Dict[str, SemanticMessage] = {}
        self.field_mappings: Dict[str, List[FieldMapping]] = {}
        self.message_mappings: Dict[str, List[MessageMapping]] = {}
        self.standard_schemas: Dict[MessageStandard, Dict] = {}
        
        # 初始化预定义的语义映射
        self._initialize_semantic_definitions()
    
    def _initialize_semantic_definitions(self):
        """初始化预定义的语义定义"""
        
        # 通用语义字段定义
        common_fields = [
            SemanticField(
                name="platform_id",
                semantic_id="sem.id.platform",
                category=SemanticCategory.IDENTIFICATION,
                field_type=FieldType.IDENTIFIER,
                description="平台标识符",
                aliases=["track_id", "unit_id", "source_id", "sender_id"]
            ),
            SemanticField(
                name="latitude",
                semantic_id="sem.pos.latitude",
                category=SemanticCategory.POSITION,
                field_type=FieldType.FLOAT,
                unit="degree",
                range_min=-90.0,
                range_max=90.0,
                description="纬度坐标",
                aliases=["lat", "y_coord"]
            ),
            SemanticField(
                name="longitude",
                semantic_id="sem.pos.longitude",
                category=SemanticCategory.POSITION,
                field_type=FieldType.FLOAT,
                unit="degree",
                range_min=-180.0,
                range_max=180.0,
                description="经度坐标",
                aliases=["lon", "lng", "x_coord"]
            ),
            SemanticField(
                name="altitude",
                semantic_id="sem.pos.altitude",
                category=SemanticCategory.POSITION,
                field_type=FieldType.FLOAT,
                unit="meter",
                description="高度",
                aliases=["alt", "height", "z_coord"]
            ),
            SemanticField(
                name="timestamp",
                semantic_id="sem.time.timestamp",
                category=SemanticCategory.TIMING,
                field_type=FieldType.TIMESTAMP,
                unit="second",
                description="时间戳",
                aliases=["time", "time_stamp", "message_time"]
            ),
            SemanticField(
                name="velocity_x",
                semantic_id="sem.nav.velocity.x",
                category=SemanticCategory.NAVIGATION,
                field_type=FieldType.FLOAT,
                unit="m/s",
                description="X轴速度",
                aliases=["vx", "vel_x", "speed_x"]
            ),
            SemanticField(
                name="velocity_y",
                semantic_id="sem.nav.velocity.y",
                category=SemanticCategory.NAVIGATION,
                field_type=FieldType.FLOAT,
                unit="m/s",
                description="Y轴速度",
                aliases=["vy", "vel_y", "speed_y"]
            ),
            SemanticField(
                name="status_code",
                semantic_id="sem.status.code",
                category=SemanticCategory.STATUS,
                field_type=FieldType.ENUM,
                description="状态代码",
                aliases=["status", "state", "mode"]
            )
        ]
        
        # 注册通用语义字段
        for field in common_fields:
            self.register_semantic_field(field)
    
    def register_semantic_field(self, field: SemanticField):
        """注册语义字段"""
        self.semantic_fields[field.semantic_id] = field
        
        # 为别名创建索引
        for alias in field.aliases:
            if alias not in self.semantic_fields:
                self.semantic_fields[alias] = field
    
    def register_semantic_message(self, message: SemanticMessage):
        """注册语义消息"""
        self.semantic_messages[message.message_id] = message
    
    def find_semantic_field(self, field_name: str) -> Optional[SemanticField]:
        """查找语义字段"""
        # 直接匹配
        if field_name in self.semantic_fields:
            return self.semantic_fields[field_name]
        
        # 模糊匹配
        field_name_lower = field_name.lower()
        for semantic_id, field in self.semantic_fields.items():
            if field_name_lower in [alias.lower() for alias in field.aliases]:
                return field
            if field_name_lower in field.name.lower():
                return field
        
        return None
    
    def register_field_mapping(self, source_field: str, target_field: str, mapping: FieldMapping):
        """注册字段映射"""
        key = f"{source_field}:{target_field}"
        if key not in self.field_mappings:
            self.field_mappings[key] = []
        self.field_mappings[key].append(mapping)
    
    def register_message_mapping(self, mapping: MessageMapping):
        """注册消息映射"""
        key = f"{mapping.source_standard.value}:{mapping.target_standard.value}"
        if key not in self.message_mappings:
            self.message_mappings[key] = []
        self.message_mappings[key].append(mapping)
        
        # 如果是双向映射，创建反向映射
        if mapping.bidirectional:
            reverse_mapping = MessageMapping(
                source_message=mapping.target_message,
                target_message=mapping.source_message,
                source_standard=mapping.target_standard,
                target_standard=mapping.source_standard,
                field_mappings=[
                    FieldMapping(
                        source_field=fm.target_field,
                        target_field=fm.source_field,
                        transform_function=self._get_reverse_transform(fm.transform_function),
                        scaling_factor=1.0/fm.scaling_factor if fm.scaling_factor else None,
                        offset=-fm.offset if fm.offset else None,
                        enum_mapping={v: k for k, v in fm.enum_mapping.items()} if fm.enum_mapping else None
                    )
                    for fm in mapping.field_mappings
                ],
                priority=mapping.priority,
                bidirectional=False  # 避免无限递归
            )
            reverse_key = f"{reverse_mapping.source_standard.value}:{reverse_mapping.target_standard.value}"
            if reverse_key not in self.message_mappings:
                self.message_mappings[reverse_key] = []
            self.message_mappings[reverse_key].append(reverse_mapping)
    
    def _get_reverse_transform(self, transform_function: Optional[str]) -> Optional[str]:
        """获取反向转换函数"""
        if not transform_function:
            return None
        
        reverse_functions = {
            "degree_to_radian": "radian_to_degree",
            "radian_to_degree": "degree_to_radian",
            "meter_to_feet": "feet_to_meter",
            "feet_to_meter": "meter_to_feet",
            "celsius_to_fahrenheit": "fahrenheit_to_celsius",
            "fahrenheit_to_celsius": "celsius_to_fahrenheit"
        }
        
        return reverse_functions.get(transform_function, transform_function)

class SemanticTransformer:
    """语义转换器"""
    
    def __init__(self, registry: SemanticRegistry):
        self.registry = registry
        self.transform_functions = {
            "degree_to_radian": lambda x: x * 3.14159265359 / 180.0,
            "radian_to_degree": lambda x: x * 180.0 / 3.14159265359,
            "meter_to_feet": lambda x: x * 3.28084,
            "feet_to_meter": lambda x: x / 3.28084,
            "celsius_to_fahrenheit": lambda x: x * 9.0/5.0 + 32.0,
            "fahrenheit_to_celsius": lambda x: (x - 32.0) * 5.0/9.0,
            "timestamp_to_epoch": lambda x: int(x),
            "epoch_to_timestamp": lambda x: float(x)
        }
    
    def transform_field_value(self, value: Any, mapping: FieldMapping) -> Any:
        """转换字段值"""
        if value is None:
            return None
        
        try:
            # 应用转换函数
            if mapping.transform_function and mapping.transform_function in self.transform_functions:
                value = self.transform_functions[mapping.transform_function](value)
            
            # 应用缩放和偏移
            if isinstance(value, (int, float)):
                if mapping.scaling_factor is not None:
                    value = value * mapping.scaling_factor
                if mapping.offset is not None:
                    value = value + mapping.offset
            
            # 应用枚举映射
            if mapping.enum_mapping and str(value) in mapping.enum_mapping:
                value = mapping.enum_mapping[str(value)]
            
            return value
            
        except Exception as e:
            logger.error(f"字段值转换失败: {e}")
            return value

class MessageRouter:
    """消息路由器"""
    
    def __init__(self, registry: SemanticRegistry, transformer: SemanticTransformer):
        self.registry = registry
        self.transformer = transformer
        self.routing_rules: List[Dict[str, Any]] = []
        self.message_handlers: Dict[str, callable] = {}
    
    def add_routing_rule(self, 
                        source_pattern: str,
                        target_standards: List[MessageStandard],
                        condition: Optional[callable] = None,
                        priority: int = 0):
        """添加路由规则"""
        rule = {
            "source_pattern": re.compile(source_pattern),
            "target_standards": target_standards,
            "condition": condition,
            "priority": priority
        }
        self.routing_rules.append(rule)
        self.routing_rules.sort(key=lambda x: x["priority"], reverse=True)
    
    def register_message_handler(self, standard: MessageStandard, handler: callable):
        """注册消息处理器"""
        self.message_handlers[standard.value] = handler
    
    def route_message(self, message: Dict[str, Any], source_standard: MessageStandard) -> List[Dict[str, Any]]:
        """路由消息"""
        routed_messages = []
        
        # 查找适用的路由规则
        for rule in self.routing_rules:
            if rule["source_pattern"].match(message.get("message_type", "")):
                if rule["condition"] is None or rule["condition"](message):
                    # 为每个目标标准转换消息
                    for target_standard in rule["target_standards"]:
                        if target_standard != source_standard:
                            converted_message = self.convert_message(
                                message, source_standard, target_standard
                            )
                            if converted_message:
                                routed_messages.append({
                                    "message": converted_message,
                                    "target_standard": target_standard,
                                    "routing_rule": rule
                                })
        
        return routed_messages
    
    def convert_message(self, 
                       message: Dict[str, Any], 
                       source_standard: MessageStandard, 
                       target_standard: MessageStandard) -> Optional[Dict[str, Any]]:
        """转换消息格式"""
        
        # 查找消息映射
        mapping_key = f"{source_standard.value}:{target_standard.value}"
        if mapping_key not in self.registry.message_mappings:
            logger.warning(f"未找到从 {source_standard.value} 到 {target_standard.value} 的消息映射")
            return None
        
        mappings = self.registry.message_mappings[mapping_key]
        
        # 查找适用的消息映射
        applicable_mapping = None
        for mapping in mappings:
            if mapping.source_message == message.get("message_type"):
                applicable_mapping = mapping
                break
        
        if not applicable_mapping:
            logger.warning(f"未找到消息类型 {message.get('message_type')} 的映射")
            return None
        
        # 执行字段转换
        converted_message = {
            "message_type": applicable_mapping.target_message,
            "source_standard": source_standard.value,
            "target_standard": target_standard.value,
            "conversion_timestamp": datetime.now().isoformat(),
            "original_message": message
        }
        
        for field_mapping in applicable_mapping.field_mappings:
            if field_mapping.source_field in message:
                source_value = message[field_mapping.source_field]
                converted_value = self.transformer.transform_field_value(source_value, field_mapping)
                converted_message[field_mapping.target_field] = converted_value
        
        return converted_message

class InteroperabilityManager:
    """互操作性管理器"""
    
    def __init__(self):
        self.registry = SemanticRegistry()
        self.transformer = SemanticTransformer(self.registry)
        self.router = MessageRouter(self.registry, self.transformer)
        self.active_mappings: Dict[str, MessageMapping] = {}
        
        # 初始化预定义的映射
        self._initialize_predefined_mappings()
    
    def _initialize_predefined_mappings(self):
        """初始化预定义的映射关系"""
        
        # MIL-STD-6016 到 MAVLink 的位置信息映射
        j20_to_global_position = MessageMapping(
            source_message="J2.0",
            target_message="GLOBAL_POSITION_INT",
            source_standard=MessageStandard.MIL_STD_6016,
            target_standard=MessageStandard.MAVLINK,
            field_mappings=[
                FieldMapping(
                    source_field="latitude",
                    target_field="lat",
                    scaling_factor=1e7,  # MAVLink uses 1e7 scale
                    transform_function="degree_to_int"
                ),
                FieldMapping(
                    source_field="longitude", 
                    target_field="lon",
                    scaling_factor=1e7,
                    transform_function="degree_to_int"
                ),
                FieldMapping(
                    source_field="altitude",
                    target_field="alt",
                    scaling_factor=1000,  # Convert to mm
                    transform_function="meter_to_mm"
                ),
                FieldMapping(
                    source_field="track_id",
                    target_field="sysid"
                )
            ],
            bidirectional=True
        )
        
        # MQTT 到 MIL-STD-6016 的状态映射
        mqtt_to_j21 = MessageMapping(
            source_message="PUBLISH",
            target_message="J2.1",
            source_standard=MessageStandard.MQTT,
            target_standard=MessageStandard.MIL_STD_6016,
            field_mappings=[
                FieldMapping(
                    source_field="client_id",
                    target_field="reporting_post"
                ),
                FieldMapping(
                    source_field="payload",
                    target_field="status_data",
                    transform_function="json_to_milstd_format"
                )
            ],
            bidirectional=False
        )
        
        # 注册映射
        self.registry.register_message_mapping(j20_to_global_position)
        self.registry.register_message_mapping(mqtt_to_j21)
        
        # 设置路由规则
        self.router.add_routing_rule(
            source_pattern=r"J2\.\d+",  # J系列消息
            target_standards=[MessageStandard.MAVLINK, MessageStandard.MQTT],
            priority=10
        )
        
        self.router.add_routing_rule(
            source_pattern=r"GLOBAL_POSITION.*",  # MAVLink位置消息
            target_standards=[MessageStandard.MIL_STD_6016],
            priority=10
        )
    
    def analyze_message_semantics(self, message: Dict[str, Any], standard: MessageStandard) -> Dict[str, Any]:
        """分析消息语义"""
        semantic_analysis = {
            "message_type": message.get("message_type", "unknown"),
            "standard": standard.value,
            "semantic_fields": {},
            "missing_semantics": [],
            "potential_mappings": []
        }
        
        # 分析每个字段的语义
        for field_name, field_value in message.items():
            semantic_field = self.registry.find_semantic_field(field_name)
            if semantic_field:
                semantic_analysis["semantic_fields"][field_name] = {
                    "semantic_id": semantic_field.semantic_id,
                    "category": semantic_field.category.value,
                    "type": semantic_field.field_type.value,
                    "value": field_value
                }
            else:
                semantic_analysis["missing_semantics"].append(field_name)
        
        # 查找潜在的映射目标
        for target_standard in MessageStandard:
            if target_standard != standard:
                mapping_key = f"{standard.value}:{target_standard.value}"
                if mapping_key in self.registry.message_mappings:
                    semantic_analysis["potential_mappings"].append(target_standard.value)
        
        return semantic_analysis
    
    def create_custom_mapping(self, 
                            source_message: str,
                            target_message: str,
                            source_standard: MessageStandard,
                            target_standard: MessageStandard,
                            field_mappings: List[Dict[str, Any]]) -> str:
        """创建自定义映射"""
        
        # 转换字段映射格式
        converted_mappings = []
        for fm in field_mappings:
            field_mapping = FieldMapping(
                source_field=fm["source_field"],
                target_field=fm["target_field"],
                transform_function=fm.get("transform_function"),
                scaling_factor=fm.get("scaling_factor"),
                offset=fm.get("offset"),
                enum_mapping=fm.get("enum_mapping")
            )
            converted_mappings.append(field_mapping)
        
        # 创建消息映射
        mapping = MessageMapping(
            source_message=source_message,
            target_message=target_message,
            source_standard=source_standard,
            target_standard=target_standard,
            field_mappings=converted_mappings,
            bidirectional=True
        )
        
        # 注册映射
        mapping_id = f"{source_standard.value}_{source_message}_to_{target_standard.value}_{target_message}"
        self.active_mappings[mapping_id] = mapping
        self.registry.register_message_mapping(mapping)
        
        logger.info(f"创建自定义映射: {mapping_id}")
        return mapping_id
    
    def process_message_with_routing(self, 
                                   message: Dict[str, Any], 
                                   source_standard: MessageStandard) -> Dict[str, Any]:
        """处理消息并进行路由"""
        
        result = {
            "original_message": message,
            "source_standard": source_standard.value,
            "semantic_analysis": self.analyze_message_semantics(message, source_standard),
            "routed_messages": [],
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # 执行消息路由
        routed_messages = self.router.route_message(message, source_standard)
        result["routed_messages"] = routed_messages
        
        # 触发消息处理器
        for routed_msg in routed_messages:
            target_standard = routed_msg["target_standard"]
            if target_standard.value in self.router.message_handlers:
                try:
                    handler = self.router.message_handlers[target_standard.value]
                    handler(routed_msg["message"])
                except Exception as e:
                    logger.error(f"消息处理器执行失败: {e}")
        
        return result
    
    def export_semantic_config(self, output_path: str):
        """导出语义配置"""
        config = {
            "semantic_fields": {
                field_id: {
                    "name": field.name,
                    "category": field.category.value,
                    "type": field.field_type.value,
                    "unit": field.unit,
                    "description": field.description,
                    "aliases": field.aliases
                }
                for field_id, field in self.registry.semantic_fields.items()
                if not field_id.startswith("sem.")  # 只导出主要语义字段
            },
            "message_mappings": {
                key: [
                    {
                        "source_message": mapping.source_message,
                        "target_message": mapping.target_message,
                        "source_standard": mapping.source_standard.value,
                        "target_standard": mapping.target_standard.value,
                        "field_mappings": [
                            {
                                "source_field": fm.source_field,
                                "target_field": fm.target_field,
                                "transform_function": fm.transform_function,
                                "scaling_factor": fm.scaling_factor,
                                "offset": fm.offset,
                                "enum_mapping": fm.enum_mapping
                            }
                            for fm in mapping.field_mappings
                        ]
                    }
                    for mapping in mappings
                ]
                for key, mappings in self.registry.message_mappings.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, sort_keys=False, allow_unicode=True)
        
        logger.info(f"语义配置已导出到: {output_path}")
    
    def import_semantic_config(self, config_path: str):
        """导入语义配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 导入语义字段
        for field_id, field_data in config.get("semantic_fields", {}).items():
            semantic_field = SemanticField(
                name=field_data["name"],
                semantic_id=field_id,
                category=SemanticCategory(field_data["category"]),
                field_type=FieldType(field_data["type"]),
                unit=field_data.get("unit"),
                description=field_data.get("description", ""),
                aliases=field_data.get("aliases", [])
            )
            self.registry.register_semantic_field(semantic_field)
        
        # 导入消息映射
        for key, mappings_data in config.get("message_mappings", {}).items():
            for mapping_data in mappings_data:
                field_mappings = [
                    FieldMapping(
                        source_field=fm["source_field"],
                        target_field=fm["target_field"],
                        transform_function=fm.get("transform_function"),
                        scaling_factor=fm.get("scaling_factor"),
                        offset=fm.get("offset"),
                        enum_mapping=fm.get("enum_mapping")
                    )
                    for fm in mapping_data["field_mappings"]
                ]
                
                message_mapping = MessageMapping(
                    source_message=mapping_data["source_message"],
                    target_message=mapping_data["target_message"],
                    source_standard=MessageStandard(mapping_data["source_standard"]),
                    target_standard=MessageStandard(mapping_data["target_standard"]),
                    field_mappings=field_mappings
                )
                
                self.registry.register_message_mapping(message_mapping)
        
        logger.info(f"语义配置已从 {config_path} 导入")

def main():
    """演示语义互操作系统"""
    print("🎯 语义互操作系统演示")
    print("=" * 50)
    
    # 创建互操作管理器
    manager = InteroperabilityManager()
    
    # 模拟一个MIL-STD-6016 J2.0消息
    j20_message = {
        "message_type": "J2.0",
        "track_id": "12345",
        "latitude": 39.9042,
        "longitude": 116.4074,
        "altitude": 50.0,
        "timestamp": 1609459200
    }
    
    print("📤 处理J2.0消息:")
    result = manager.process_message_with_routing(j20_message, MessageStandard.MIL_STD_6016)
    print(f"   原始消息: {j20_message}")
    print(f"   路由到 {len(result['routed_messages'])} 个目标标准")
    
    for routed in result['routed_messages']:
        print(f"   → {routed['target_standard'].value}: {routed['message']['message_type']}")
    
    # 导出配置
    manager.export_semantic_config("semantic_config.yaml")
    print("\\n✅ 语义配置已导出")

if __name__ == "__main__":
    main()
