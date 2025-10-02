#!/usr/bin/env python3
"""
CDM语义互操作API接口
提供四层法CDM系统的完整Web API
"""
from fastapi import APIRouter, HTTPException, Body, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import json
import logging

from cdm_system import (
    CDMInteropSystem, CDMConcept, DataType, Unit, CoordinateFrame,
    MappingRule, ValidationResult
)

router = APIRouter(prefix="/api/cdm", tags=["cdm_interoperability"])
logger = logging.getLogger(__name__)

# 全局CDM系统实例
cdm_system = CDMInteropSystem()

# Pydantic模型定义
class ConceptInput(BaseModel):
    """CDM概念输入模型"""
    path: str = Field(..., description="概念路径，如 Track.Identity")
    data_type: str = Field(..., description="数据类型")
    unit: Optional[str] = Field(None, description="单位")
    value_range: Optional[Tuple[float, float]] = Field(None, description="取值范围")
    resolution: Optional[float] = Field(None, description="分辨率")
    coordinate_frame: Optional[str] = Field(None, description="坐标参考系")
    enum_values: Optional[Dict[str, str]] = Field(None, description="枚举值")
    description: str = Field("", description="描述")
    confidence: float = Field(1.0, description="置信度")
    source: str = Field("", description="来源")

class MappingRuleInput(BaseModel):
    """映射规则输入模型"""
    source_field: str = Field(..., description="源字段")
    cdm_path: str = Field(..., description="CDM路径")
    target_field: str = Field(..., description="目标字段")
    unit_conversion: Optional[Tuple[str, str]] = Field(None, description="单位转换")
    scale_factor: Optional[float] = Field(None, description="缩放因子")
    offset: Optional[float] = Field(None, description="偏移量")
    enum_mapping: Optional[Dict[str, str]] = Field(None, description="枚举映射")
    bit_range: Optional[Tuple[int, int]] = Field(None, description="位范围")
    condition: Optional[str] = Field(None, description="条件")
    default_value: Optional[Any] = Field(None, description="默认值")
    version: str = Field("1.0", description="版本")
    author: str = Field("", description="作者")

class MessageConversionInput(BaseModel):
    """消息转换输入模型"""
    source_message: Dict[str, Any] = Field(..., description="源消息")
    source_protocol: str = Field(..., description="源协议")
    target_protocol: str = Field(..., description="目标协议")
    message_type: str = Field(..., description="消息类型")

class GoldenSampleInput(BaseModel):
    """金标准样例输入模型"""
    sample_name: str = Field(..., description="样例名称")
    source_message: Dict[str, Any] = Field(..., description="源消息")
    expected_message: Dict[str, Any] = Field(..., description="期望消息")
    source_protocol: str = Field(..., description="源协议")
    target_protocol: str = Field(..., description="目标协议")
    message_type: str = Field(..., description="消息类型")

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "CDM语义互操作系统运行正常",
        "timestamp": datetime.now().isoformat(),
        "cdm_concepts": len(cdm_system.cdm_registry.concepts),
        "mapping_rules": len(cdm_system.mapping_registry.mappings)
    }

@router.get("/concepts")
async def get_cdm_concepts(
    category: Optional[str] = Query(None, description="概念类别过滤"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """获取CDM概念列表"""
    try:
        concepts = []
        
        for path, concept in cdm_system.cdm_registry.concepts.items():
            # 应用过滤器
            if category and category.lower() not in path.lower():
                continue
            
            if search and search.lower() not in path.lower() and search.lower() not in concept.description.lower():
                continue
            
            concepts.append({
                "path": concept.path,
                "data_type": concept.data_type.value,
                "unit": concept.unit.value if concept.unit else None,
                "value_range": concept.value_range,
                "resolution": concept.resolution,
                "coordinate_frame": concept.coordinate_frame.value if concept.coordinate_frame else None,
                "enum_values": concept.enum_values,
                "description": concept.description,
                "confidence": concept.confidence,
                "source": concept.source,
                "version": concept.version,
                "created_at": concept.created_at.isoformat()
            })
        
        return {
            "success": True,
            "concepts": concepts,
            "total": len(concepts)
        }
        
    except Exception as e:
        logger.error(f"获取CDM概念失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/concepts")
async def create_cdm_concept(concept_input: ConceptInput):
    """创建CDM概念"""
    try:
        # 验证数据类型
        try:
            data_type = DataType(concept_input.data_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"不支持的数据类型: {concept_input.data_type}")
        
        # 验证单位
        unit = None
        if concept_input.unit:
            try:
                unit = Unit(concept_input.unit)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"不支持的单位: {concept_input.unit}")
        
        # 验证坐标参考系
        coordinate_frame = None
        if concept_input.coordinate_frame:
            try:
                coordinate_frame = CoordinateFrame(concept_input.coordinate_frame)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"不支持的坐标参考系: {concept_input.coordinate_frame}")
        
        # 创建CDM概念
        concept = CDMConcept(
            path=concept_input.path,
            data_type=data_type,
            unit=unit,
            value_range=concept_input.value_range,
            resolution=concept_input.resolution,
            coordinate_frame=coordinate_frame,
            enum_values=concept_input.enum_values,
            description=concept_input.description,
            confidence=concept_input.confidence,
            source=concept_input.source
        )
        
        # 注册概念
        cdm_system.cdm_registry.register_concept(concept)
        
        return {
            "success": True,
            "message": "CDM概念创建成功",
            "concept": {
                "path": concept.path,
                "data_type": concept.data_type.value,
                "unit": concept.unit.value if concept.unit else None,
                "description": concept.description
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建CDM概念失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/concepts/{concept_path}")
async def get_cdm_concept(concept_path: str):
    """获取特定CDM概念"""
    try:
        concept = cdm_system.cdm_registry.get_concept(concept_path)
        
        if not concept:
            raise HTTPException(status_code=404, detail=f"未找到CDM概念: {concept_path}")
        
        return {
            "success": True,
            "concept": {
                "path": concept.path,
                "data_type": concept.data_type.value,
                "unit": concept.unit.value if concept.unit else None,
                "value_range": concept.value_range,
                "resolution": concept.resolution,
                "coordinate_frame": concept.coordinate_frame.value if concept.coordinate_frame else None,
                "enum_values": concept.enum_values,
                "description": concept.description,
                "confidence": concept.confidence,
                "source": concept.source,
                "version": concept.version,
                "created_at": concept.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取CDM概念失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mappings")
async def create_mapping_rule(
    source_protocol: str = Body(..., description="源协议"),
    target_protocol: str = Body(..., description="目标协议"),
    message_type: str = Body(..., description="消息类型"),
    rules: List[MappingRuleInput] = Body(..., description="映射规则列表")
):
    """创建映射规则"""
    try:
        # 转换映射规则
        mapping_rules = []
        for rule_input in rules:
            # 验证单位转换
            unit_conversion = None
            if rule_input.unit_conversion:
                try:
                    from_unit = Unit(rule_input.unit_conversion[0])
                    to_unit = Unit(rule_input.unit_conversion[1])
                    unit_conversion = (from_unit, to_unit)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"无效的单位转换: {e}")
            
            rule = MappingRule(
                source_field=rule_input.source_field,
                cdm_path=rule_input.cdm_path,
                target_field=rule_input.target_field,
                unit_conversion=unit_conversion,
                scale_factor=rule_input.scale_factor,
                offset=rule_input.offset,
                enum_mapping=rule_input.enum_mapping,
                bit_range=rule_input.bit_range,
                condition=rule_input.condition,
                default_value=rule_input.default_value,
                version=rule_input.version,
                author=rule_input.author
            )
            mapping_rules.append(rule)
        
        # 注册映射
        cdm_system.mapping_registry.register_mapping(
            source_protocol, target_protocol, {message_type: mapping_rules}
        )
        
        return {
            "success": True,
            "message": "映射规则创建成功",
            "mapping_key": f"{source_protocol}→{target_protocol}",
            "message_type": message_type,
            "rule_count": len(mapping_rules),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建映射规则失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings")
async def get_mapping_rules(
    source_protocol: Optional[str] = Query(None, description="源协议过滤"),
    target_protocol: Optional[str] = Query(None, description="目标协议过滤")
):
    """获取映射规则列表"""
    try:
        mappings = []
        
        for mapping_key, mapping in cdm_system.mapping_registry.mappings.items():
            # 应用过滤器
            if source_protocol and mapping.source_protocol != source_protocol:
                continue
            if target_protocol and mapping.target_protocol != target_protocol:
                continue
            
            mappings.append({
                "mapping_key": mapping_key,
                "source_protocol": mapping.source_protocol,
                "target_protocol": mapping.target_protocol,
                "version": mapping.version,
                "author": mapping.author,
                "created_at": mapping.created_at.isoformat(),
                "message_types": list(mapping.message_mappings.keys()),
                "total_rules": sum(len(rules) for rules in mapping.message_mappings.values())
            })
        
        return {
            "success": True,
            "mappings": mappings,
            "total": len(mappings)
        }
        
    except Exception as e:
        logger.error(f"获取映射规则失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings/{source_protocol}/{target_protocol}")
async def get_specific_mappings(
    source_protocol: str = Path(..., description="源协议"),
    target_protocol: str = Path(..., description="目标协议")
):
    """获取特定协议间的详细映射规则"""
    try:
        mapping_key = f"{source_protocol}→{target_protocol}"
        
        if mapping_key not in cdm_system.mapping_registry.mappings:
            return {
                "success": True,
                "mappings": [],
                "message": f"未找到从 {source_protocol} 到 {target_protocol} 的映射"
            }
        
        mapping = cdm_system.mapping_registry.mappings[mapping_key]
        detailed_mappings = {}
        
        for message_type, rules in mapping.message_mappings.items():
            detailed_mappings[message_type] = [
                {
                    "source_field": rule.source_field,
                    "cdm_path": rule.cdm_path,
                    "target_field": rule.target_field,
                    "unit_conversion": [rule.unit_conversion[0].value, rule.unit_conversion[1].value] if rule.unit_conversion else None,
                    "scale_factor": rule.scale_factor,
                    "offset": rule.offset,
                    "enum_mapping": rule.enum_mapping,
                    "bit_range": rule.bit_range,
                    "condition": rule.condition,
                    "default_value": rule.default_value,
                    "version": rule.version,
                    "author": rule.author
                }
                for rule in rules
            ]
        
        return {
            "success": True,
            "mapping_key": mapping_key,
            "source_protocol": mapping.source_protocol,
            "target_protocol": mapping.target_protocol,
            "version": mapping.version,
            "mappings": detailed_mappings
        }
        
    except Exception as e:
        logger.error(f"获取特定映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert")
async def convert_message(conversion_input: MessageConversionInput):
    """转换消息"""
    try:
        result = cdm_system.process_message(
            source_message=conversion_input.source_message,
            source_protocol=conversion_input.source_protocol,
            target_protocol=conversion_input.target_protocol,
            message_type=conversion_input.message_type
        )
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"消息转换失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_concept_value(
    concept_path: str = Body(..., description="概念路径"),
    value: Any = Body(..., description="要校验的值")
):
    """校验概念值"""
    try:
        validation_result = cdm_system.validator.validate_concept_value(concept_path, value)
        
        return {
            "success": True,
            "concept_path": concept_path,
            "value": value,
            "validation": {
                "is_valid": validation_result.is_valid,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "metrics": validation_result.metrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"概念值校验失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/golden-samples")
async def add_golden_sample(golden_sample: GoldenSampleInput):
    """添加金标准样例"""
    try:
        sample = {
            "sample_name": golden_sample.sample_name,
            "source_message": golden_sample.source_message,
            "expected_message": golden_sample.expected_message,
            "source_protocol": golden_sample.source_protocol,
            "target_protocol": golden_sample.target_protocol,
            "message_type": golden_sample.message_type,
            "added_at": datetime.now().isoformat()
        }
        
        cdm_system.validator.add_golden_sample(sample)
        
        return {
            "success": True,
            "message": "金标准样例添加成功",
            "sample_name": golden_sample.sample_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"添加金标准样例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/golden-samples/regression")
async def run_golden_set_regression():
    """运行金标准回归测试"""
    try:
        validation_result = cdm_system.validator.run_golden_set_regression()
        
        return {
            "success": True,
            "regression_result": {
                "is_valid": validation_result.is_valid,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "metrics": validation_result.metrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"金标准回归测试失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unit-conversions")
async def get_unit_conversions():
    """获取单位转换表"""
    try:
        conversions = {}
        
        for (from_unit, to_unit), factor in cdm_system.cdm_registry.unit_conversions.items():
            key = f"{from_unit.value}→{to_unit.value}"
            conversions[key] = {
                "from_unit": from_unit.value,
                "to_unit": to_unit.value,
                "conversion_factor": factor,
                "formula": f"value * {factor}"
            }
        
        return {
            "success": True,
            "conversions": conversions,
            "total": len(conversions)
        }
        
    except Exception as e:
        logger.error(f"获取单位转换表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-schema")
async def export_cdm_schema():
    """导出CDM模式"""
    try:
        output_path = f"cdm_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        cdm_system.export_cdm_schema(output_path)
        
        return {
            "success": True,
            "message": "CDM模式导出成功",
            "file_path": output_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"导出CDM模式失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_system_statistics():
    """获取系统统计信息"""
    try:
        # 统计CDM概念
        concepts_by_category = {}
        for path, concept in cdm_system.cdm_registry.concepts.items():
            category = path.split('.')[0]  # 取第一级作为类别
            if category not in concepts_by_category:
                concepts_by_category[category] = 0
            concepts_by_category[category] += 1
        
        # 统计映射规则
        total_mappings = sum(
            len(rules) for mapping in cdm_system.mapping_registry.mappings.values()
            for rules in mapping.message_mappings.values()
        )
        
        # 统计协议支持
        supported_protocols = set()
        for mapping in cdm_system.mapping_registry.mappings.values():
            supported_protocols.add(mapping.source_protocol)
            supported_protocols.add(mapping.target_protocol)
        
        return {
            "success": True,
            "statistics": {
                "cdm_concepts": {
                    "total": len(cdm_system.cdm_registry.concepts),
                    "by_category": concepts_by_category
                },
                "mapping_rules": {
                    "total": total_mappings,
                    "protocol_pairs": len(cdm_system.mapping_registry.mappings)
                },
                "supported_protocols": list(supported_protocols),
                "unit_conversions": len(cdm_system.cdm_registry.unit_conversions),
                "golden_samples": len(cdm_system.validator.golden_set)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 集成到主应用的函数
def include_cdm_routes(app):
    """将CDM路由添加到FastAPI应用"""
    app.include_router(router)
    logger.info("CDM语义互操作API路由已加载")
