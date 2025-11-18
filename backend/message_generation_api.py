#!/usr/bin/env python3
"""
消息生成API模块
提供消息实例生成、二进制编码、异常注入等功能的API接口
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json

try:
    from backend.generators.message_instance_generator import MessageInstanceGenerator, GenerationMode
    from backend.generators.anomaly_generator import AnomalyMessageGenerator, AnomalyStrategy
    from backend.encoders.binary_encoder import BinaryMessageEncoder, BinaryFormat
    from backend.schema.message_definition import MessageDefinition
    GENERATORS_AVAILABLE = True
except ImportError as e:
    print(f"消息生成模块导入失败: {e}")
    GENERATORS_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/message-generation", tags=["消息生成"])


# ---------- 数据模型 ----------
class GenerateInstanceRequest(BaseModel):
    """生成消息实例请求"""
    message_definition: Dict[str, Any]  # MessageDefinition的JSON格式
    mode: str = "default"  # default/random/boundary/anomaly
    fill_header: bool = True
    count: int = 1
    custom_values: Optional[Dict[str, Any]] = None
    random_seed: Optional[int] = None


class GenerateInstanceResponse(BaseModel):
    """生成消息实例响应"""
    success: bool
    instances: List[Dict[str, Any]]
    mode: str
    count: int


class InjectAnomalyRequest(BaseModel):
    """注入异常请求"""
    message_definition: Dict[str, Any]
    instance: Dict[str, Any]
    strategy: str = "random"  # missing_field/type_mismatch/out_of_bounds/encoding_error/random
    target_field: Optional[str] = None
    count: int = 1


class InjectAnomalyResponse(BaseModel):
    """注入异常响应"""
    success: bool
    anomalous_instances: List[Dict[str, Any]]
    strategy: str
    count: int


class EncodeBinaryRequest(BaseModel):
    """编码二进制请求"""
    message_definition: Dict[str, Any]
    instance: Dict[str, Any]
    format_type: str = "raw"  # protobuf/tlv/asn1/raw
    endianness: str = "big"  # big/little
    alignment: int = 4


class EncodeBinaryResponse(BaseModel):
    """编码二进制响应"""
    success: bool
    binary_data: str  # Base64编码的二进制数据
    format_type: str
    size_bytes: int


# ---------- API接口 ----------
@router.post("/generate-instance", response_model=GenerateInstanceResponse)
async def generate_instance(request: GenerateInstanceRequest):
    """
    生成消息实例
    
    支持默认值、随机值、边界值、异常值生成
    """
    if not GENERATORS_AVAILABLE:
        raise HTTPException(status_code=503, detail="消息生成模块不可用")
    
    try:
        # 解析消息定义
        message_def = MessageDefinition.from_json(json.dumps(request.message_definition))
        
        # 创建生成器
        mode = GenerationMode(request.mode)
        generator = MessageInstanceGenerator(mode=mode)
        
        if request.random_seed:
            generator.set_random_seed(request.random_seed)
        
        # 生成实例
        if request.count > 1:
            instances = generator.generate_batch(
                message_def, 
                count=request.count,
                fill_header=request.fill_header
            )
        else:
            instance = generator.generate(
                message_def,
                fill_header=request.fill_header,
                custom_values=request.custom_values
            )
            instances = [instance]
        
        return GenerateInstanceResponse(
            success=True,
            instances=instances,
            mode=request.mode,
            count=len(instances)
        )
    except Exception as e:
        logger.error(f"生成消息实例失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inject-anomaly", response_model=InjectAnomalyResponse)
async def inject_anomaly(request: InjectAnomalyRequest):
    """
    注入异常到消息实例
    
    支持多种异常注入策略：字段缺失、类型错误、越界值、编码错误等
    """
    if not GENERATORS_AVAILABLE:
        raise HTTPException(status_code=503, detail="消息生成模块不可用")
    
    try:
        # 解析消息定义
        message_def = MessageDefinition.from_json(json.dumps(request.message_definition))
        
        # 创建异常生成器
        strategy = AnomalyStrategy(request.strategy)
        anomaly_generator = AnomalyMessageGenerator(strategy=strategy)
        
        # 生成异常实例
        if request.count > 1:
            anomalous_instances = anomaly_generator.generate_anomaly_batch(
                message_def,
                request.instance,
                count=request.count
            )
        else:
            anomalous_instance = anomaly_generator.inject_anomaly(
                message_def,
                request.instance,
                target_field=request.target_field
            )
            anomalous_instances = [anomalous_instance]
        
        return InjectAnomalyResponse(
            success=True,
            anomalous_instances=anomalous_instances,
            strategy=request.strategy,
            count=len(anomalous_instances)
        )
    except Exception as e:
        logger.error(f"注入异常失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encode-binary", response_model=EncodeBinaryResponse)
async def encode_binary(request: EncodeBinaryRequest):
    """
    编码消息实例为二进制格式
    
    支持Protocol Buffer、TLV、ASN.1、原始字节对齐格式
    """
    if not GENERATORS_AVAILABLE:
        raise HTTPException(status_code=503, detail="消息生成模块不可用")
    
    try:
        # 解析消息定义
        message_def = MessageDefinition.from_json(json.dumps(request.message_definition))
        
        # 创建编码器
        format_type = BinaryFormat(request.format_type)
        encoder = BinaryMessageEncoder(
            format_type=format_type,
            endianness=request.endianness
        )
        
        # 编码为二进制
        binary_data = encoder.encode(
            message_def,
            request.instance,
            alignment=request.alignment
        )
        
        # 转换为Base64
        import base64
        binary_base64 = base64.b64encode(binary_data).decode('utf-8')
        
        return EncodeBinaryResponse(
            success=True,
            binary_data=binary_base64,
            format_type=request.format_type,
            size_bytes=len(binary_data)
        )
    except Exception as e:
        logger.error(f"编码二进制失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generation-modes")
async def get_generation_modes():
    """获取支持的生成模式列表"""
    return {
        "success": True,
        "modes": [
            {"value": "default", "description": "默认值生成"},
            {"value": "random", "description": "随机值生成"},
            {"value": "boundary", "description": "边界值生成"},
            {"value": "anomaly", "description": "异常值生成"},
        ]
    }


@router.get("/anomaly-strategies")
async def get_anomaly_strategies():
    """获取支持的异常注入策略列表"""
    return {
        "success": True,
        "strategies": [
            {"value": "missing_field", "description": "字段缺失"},
            {"value": "type_mismatch", "description": "类型错误"},
            {"value": "out_of_bounds", "description": "越界值"},
            {"value": "encoding_error", "description": "编码错误"},
            {"value": "nested_level", "description": "嵌套层级错误"},
            {"value": "bit_overflow", "description": "位段溢出"},
            {"value": "random", "description": "随机异常"},
        ]
    }


@router.get("/binary-formats")
async def get_binary_formats():
    """获取支持的二进制格式列表"""
    return {
        "success": True,
        "formats": [
            {"value": "raw", "description": "原始字节对齐格式"},
            {"value": "protobuf", "description": "Protocol Buffer格式"},
            {"value": "tlv", "description": "TLV (Tag-Length-Value)格式"},
            {"value": "asn1", "description": "ASN.1格式"},
        ]
    }


def include_message_generation_routes(app):
    """包含消息生成路由到FastAPI应用"""
    if GENERATORS_AVAILABLE:
        app.include_router(router)
        print("✓ 消息生成API模块已加载")
    else:
        print("✗ 消息生成API模块不可用（依赖未安装）")

