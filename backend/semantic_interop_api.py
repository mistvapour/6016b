#!/usr/bin/env python3
"""
语义互操作API接口
提供语义映射、消息转发和人工标注的Web接口
"""
from fastapi import APIRouter, HTTPException, Body, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import logging

from semantic_interop_system import (
    InteroperabilityManager, MessageStandard, SemanticCategory, 
    FieldType, FieldMapping, MessageMapping
)

router = APIRouter(prefix="/api/semantic", tags=["semantic_interoperability"])
logger = logging.getLogger(__name__)

# 全局互操作管理器实例
interop_manager = InteroperabilityManager()

# Pydantic模型定义
class MessageInput(BaseModel):
    """消息输入模型"""
    message: Dict[str, Any] = Field(..., description="消息内容")
    standard: str = Field(..., description="消息标准")
    message_type: Optional[str] = Field(None, description="消息类型")

class FieldMappingInput(BaseModel):
    """字段映射输入模型"""
    source_field: str = Field(..., description="源字段名")
    target_field: str = Field(..., description="目标字段名")
    transform_function: Optional[str] = Field(None, description="转换函数")
    scaling_factor: Optional[float] = Field(None, description="缩放因子")
    offset: Optional[float] = Field(None, description="偏移量")
    enum_mapping: Optional[Dict[str, str]] = Field(None, description="枚举映射")

class MessageMappingInput(BaseModel):
    """消息映射输入模型"""
    source_message: str = Field(..., description="源消息类型")
    target_message: str = Field(..., description="目标消息类型")
    source_standard: str = Field(..., description="源标准")
    target_standard: str = Field(..., description="目标标准")
    field_mappings: List[FieldMappingInput] = Field(..., description="字段映射列表")

class SemanticAnnotation(BaseModel):
    """语义标注模型"""
    field_name: str = Field(..., description="字段名")
    semantic_id: str = Field(..., description="语义标识符")
    category: str = Field(..., description="语义类别")
    field_type: str = Field(..., description="字段类型")
    unit: Optional[str] = Field(None, description="单位")
    description: str = Field("", description="描述")
    aliases: List[str] = Field(default_factory=list, description="别名列表")

class RoutingRule(BaseModel):
    """路由规则模型"""
    source_pattern: str = Field(..., description="源消息模式(正则表达式)")
    target_standards: List[str] = Field(..., description="目标标准列表")
    priority: int = Field(0, description="优先级")

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "语义互操作系统运行正常",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/standards")
async def get_supported_standards():
    """获取支持的消息标准"""
    try:
        standards = [
            {
                "value": standard.value,
                "name": standard.name,
                "description": f"{standard.value} 消息标准"
            }
            for standard in MessageStandard
        ]
        
        return {
            "success": True,
            "standards": standards,
            "total": len(standards)
        }
        
    except Exception as e:
        logger.error(f"获取支持标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/semantic-categories")
async def get_semantic_categories():
    """获取语义类别"""
    try:
        categories = [
            {
                "value": category.value,
                "name": category.name,
                "description": f"{category.value} 类别"
            }
            for category in SemanticCategory
        ]
        
        return {
            "success": True,
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"获取语义类别失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/field-types")
async def get_field_types():
    """获取字段类型"""
    try:
        field_types = [
            {
                "value": field_type.value,
                "name": field_type.name,
                "description": f"{field_type.value} 类型"
            }
            for field_type in FieldType
        ]
        
        return {
            "success": True,
            "field_types": field_types,
            "total": len(field_types)
        }
        
    except Exception as e:
        logger.error(f"获取字段类型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-message")
async def analyze_message_semantics(message_input: MessageInput):
    """分析消息语义"""
    try:
        # 验证消息标准
        try:
            standard = MessageStandard(message_input.standard)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的消息标准: {message_input.standard}"
            )
        
        # 分析消息语义
        analysis = interop_manager.analyze_message_semantics(
            message_input.message, 
            standard
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"消息语义分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-message")
async def process_message_with_routing(message_input: MessageInput):
    """处理消息并执行路由"""
    try:
        # 验证消息标准
        try:
            standard = MessageStandard(message_input.standard)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的消息标准: {message_input.standard}"
            )
        
        # 处理消息
        result = interop_manager.process_message_with_routing(
            message_input.message,
            standard
        )
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"消息处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-mapping")
async def create_message_mapping(mapping_input: MessageMappingInput):
    """创建消息映射"""
    try:
        # 验证消息标准
        try:
            source_standard = MessageStandard(mapping_input.source_standard)
            target_standard = MessageStandard(mapping_input.target_standard)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"不支持的消息标准: {e}")
        
        # 转换字段映射
        field_mappings = [
            {
                "source_field": fm.source_field,
                "target_field": fm.target_field,
                "transform_function": fm.transform_function,
                "scaling_factor": fm.scaling_factor,
                "offset": fm.offset,
                "enum_mapping": fm.enum_mapping
            }
            for fm in mapping_input.field_mappings
        ]
        
        # 创建映射
        mapping_id = interop_manager.create_custom_mapping(
            source_message=mapping_input.source_message,
            target_message=mapping_input.target_message,
            source_standard=source_standard,
            target_standard=target_standard,
            field_mappings=field_mappings
        )
        
        return {
            "success": True,
            "mapping_id": mapping_id,
            "message": "消息映射创建成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建消息映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings")
async def get_message_mappings(
    source_standard: Optional[str] = Query(None, description="源标准过滤"),
    target_standard: Optional[str] = Query(None, description="目标标准过滤")
):
    """获取消息映射列表"""
    try:
        mappings = []
        
        for key, mapping_list in interop_manager.registry.message_mappings.items():
            for mapping in mapping_list:
                # 应用过滤器
                if source_standard and mapping.source_standard.value != source_standard:
                    continue
                if target_standard and mapping.target_standard.value != target_standard:
                    continue
                
                mappings.append({
                    "source_message": mapping.source_message,
                    "target_message": mapping.target_message,
                    "source_standard": mapping.source_standard.value,
                    "target_standard": mapping.target_standard.value,
                    "field_count": len(mapping.field_mappings),
                    "bidirectional": mapping.bidirectional,
                    "priority": mapping.priority
                })
        
        return {
            "success": True,
            "mappings": mappings,
            "total": len(mappings)
        }
        
    except Exception as e:
        logger.error(f"获取消息映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings/{source_standard}/{target_standard}")
async def get_specific_mappings(
    source_standard: str = Path(..., description="源标准"),
    target_standard: str = Path(..., description="目标标准")
):
    """获取特定标准间的详细映射"""
    try:
        mapping_key = f"{source_standard}:{target_standard}"
        
        if mapping_key not in interop_manager.registry.message_mappings:
            return {
                "success": True,
                "mappings": [],
                "message": f"未找到从 {source_standard} 到 {target_standard} 的映射"
            }
        
        mappings = []
        for mapping in interop_manager.registry.message_mappings[mapping_key]:
            field_mappings = [
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
            
            mappings.append({
                "source_message": mapping.source_message,
                "target_message": mapping.target_message,
                "source_standard": mapping.source_standard.value,
                "target_standard": mapping.target_standard.value,
                "field_mappings": field_mappings,
                "bidirectional": mapping.bidirectional,
                "priority": mapping.priority
            })
        
        return {
            "success": True,
            "mappings": mappings,
            "total": len(mappings)
        }
        
    except Exception as e:
        logger.error(f"获取特定映射失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/semantic-annotation")
async def create_semantic_annotation(annotation: SemanticAnnotation):
    """创建语义标注"""
    try:
        from semantic_interop_system import SemanticField
        
        # 验证语义类别和字段类型
        try:
            category = SemanticCategory(annotation.category)
            field_type = FieldType(annotation.field_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的类别或类型: {e}")
        
        # 创建语义字段
        semantic_field = SemanticField(
            name=annotation.field_name,
            semantic_id=annotation.semantic_id,
            category=category,
            field_type=field_type,
            unit=annotation.unit,
            description=annotation.description,
            aliases=annotation.aliases
        )
        
        # 注册语义字段
        interop_manager.registry.register_semantic_field(semantic_field)
        
        return {
            "success": True,
            "message": "语义标注创建成功",
            "semantic_field": {
                "name": semantic_field.name,
                "semantic_id": semantic_field.semantic_id,
                "category": semantic_field.category.value,
                "type": semantic_field.field_type.value
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建语义标注失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/semantic-fields")
async def get_semantic_fields(
    category: Optional[str] = Query(None, description="语义类别过滤"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """获取语义字段列表"""
    try:
        fields = []
        
        for semantic_id, field in interop_manager.registry.semantic_fields.items():
            # 跳过别名条目
            if semantic_id != field.semantic_id:
                continue
            
            # 应用过滤器
            if category and field.category.value != category:
                continue
            
            if search and search.lower() not in field.name.lower() and search.lower() not in field.description.lower():
                continue
            
            fields.append({
                "semantic_id": field.semantic_id,
                "name": field.name,
                "category": field.category.value,
                "type": field.field_type.value,
                "unit": field.unit,
                "description": field.description,
                "aliases": field.aliases
            })
        
        return {
            "success": True,
            "fields": fields,
            "total": len(fields)
        }
        
    except Exception as e:
        logger.error(f"获取语义字段失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/routing-rule")
async def add_routing_rule(rule: RoutingRule):
    """添加路由规则"""
    try:
        # 验证目标标准
        target_standards = []
        for standard_str in rule.target_standards:
            try:
                standard = MessageStandard(standard_str)
                target_standards.append(standard)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的目标标准: {standard_str}"
                )
        
        # 添加路由规则
        interop_manager.router.add_routing_rule(
            source_pattern=rule.source_pattern,
            target_standards=target_standards,
            priority=rule.priority
        )
        
        return {
            "success": True,
            "message": "路由规则添加成功",
            "rule": {
                "source_pattern": rule.source_pattern,
                "target_standards": rule.target_standards,
                "priority": rule.priority
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加路由规则失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing-rules")
async def get_routing_rules():
    """获取路由规则列表"""
    try:
        rules = []
        
        for rule in interop_manager.router.routing_rules:
            rules.append({
                "source_pattern": rule["source_pattern"].pattern,
                "target_standards": [std.value for std in rule["target_standards"]],
                "priority": rule["priority"],
                "has_condition": rule["condition"] is not None
            })
        
        return {
            "success": True,
            "rules": rules,
            "total": len(rules)
        }
        
    except Exception as e:
        logger.error(f"获取路由规则失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-config")
async def export_semantic_config():
    """导出语义配置"""
    try:
        output_path = f"semantic_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        interop_manager.export_semantic_config(output_path)
        
        return {
            "success": True,
            "message": "语义配置导出成功",
            "file_path": output_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"导出语义配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-config")
async def import_semantic_config(config_path: str = Body(..., embed=True)):
    """导入语义配置"""
    try:
        interop_manager.import_semantic_config(config_path)
        
        return {
            "success": True,
            "message": "语义配置导入成功",
            "config_path": config_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"配置文件不存在: {config_path}")
    except Exception as e:
        logger.error(f"导入语义配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_system_statistics():
    """获取系统统计信息"""
    try:
        # 统计语义字段
        semantic_fields_count = len([
            f for f in interop_manager.registry.semantic_fields.values()
            if f.semantic_id.startswith("sem.")
        ])
        
        # 统计消息映射
        total_mappings = sum(
            len(mappings) for mappings in interop_manager.registry.message_mappings.values()
        )
        
        # 统计路由规则
        routing_rules_count = len(interop_manager.router.routing_rules)
        
        # 按标准统计映射
        mappings_by_standard = {}
        for key, mappings in interop_manager.registry.message_mappings.items():
            source_std, target_std = key.split(":")
            if source_std not in mappings_by_standard:
                mappings_by_standard[source_std] = {}
            mappings_by_standard[source_std][target_std] = len(mappings)
        
        return {
            "success": True,
            "statistics": {
                "semantic_fields": semantic_fields_count,
                "message_mappings": total_mappings,
                "routing_rules": routing_rules_count,
                "supported_standards": len(MessageStandard),
                "semantic_categories": len(SemanticCategory),
                "field_types": len(FieldType),
                "mappings_by_standard": mappings_by_standard
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 集成到主应用的函数
def include_semantic_routes(app):
    """将语义互操作路由添加到FastAPI应用"""
    app.include_router(router)
    logger.info("语义互操作API路由已加载")
