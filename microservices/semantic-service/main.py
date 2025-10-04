#!/usr/bin/env python3
"""
语义互操作微服务
负责跨标准语义分析和消息转换
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import logging
import json
from datetime import datetime
import uuid

# 导入语义处理模块
import sys
sys.path.append('/app')
from semantic_analyzer import SemanticAnalyzer
from message_converter import MessageConverter
from mapping_manager import MappingManager

# 配置
SERVICE_CONFIG = {
    "name": "semantic-service",
    "version": "1.0.0",
    "port": 8002,
    "supported_protocols": ["MIL-STD-6016", "MAVLink", "MQTT", "XML", "JSON"],
    "max_message_size": 10 * 1024 * 1024,  # 10MB
    "processing_timeout": 60  # 1分钟
}

# 创建FastAPI应用
app = FastAPI(
    title="Semantic Interoperability Service",
    version=SERVICE_CONFIG["version"],
    description="跨标准语义互操作微服务"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据模型
class MessageAnalysisRequest(BaseModel):
    message: Dict[str, Any]
    source_protocol: str
    target_protocol: Optional[str] = None
    analysis_type: str = "full"  # full, quick, semantic_only

class MessageConversionRequest(BaseModel):
    source_message: Dict[str, Any]
    source_protocol: str
    target_protocol: str
    target_message_type: Optional[str] = None
    mapping_rules: Optional[Dict[str, Any]] = None

class SemanticAnnotationRequest(BaseModel):
    field_name: str
    field_value: Any
    context: Optional[Dict[str, Any]] = None
    confidence_threshold: float = 0.7

class MappingRuleRequest(BaseModel):
    source_protocol: str
    target_protocol: str
    message_type: str
    rules: List[Dict[str, Any]]
    version: str = "1.0"
    description: Optional[str] = None

class ProcessingResult(BaseModel):
    task_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# 全局变量
processing_tasks: Dict[str, ProcessingResult] = {}
semantic_analyzer = SemanticAnalyzer()
message_converter = MessageConverter()
mapping_manager = MappingManager()

# 健康检查
@app.get("/health")
async def health_check():
    """服务健康检查"""
    return {
        "service": SERVICE_CONFIG["name"],
        "status": "healthy",
        "version": SERVICE_CONFIG["version"],
        "timestamp": datetime.now().isoformat(),
        "supported_protocols": SERVICE_CONFIG["supported_protocols"]
    }

# 服务信息
@app.get("/info")
async def service_info():
    """获取服务信息"""
    return {
        "name": SERVICE_CONFIG["name"],
        "version": SERVICE_CONFIG["version"],
        "supported_protocols": SERVICE_CONFIG["supported_protocols"],
        "max_message_size": SERVICE_CONFIG["max_message_size"],
        "processing_timeout": SERVICE_CONFIG["processing_timeout"]
    }

# 消息语义分析
@app.post("/analyze", response_model=ProcessingResult)
async def analyze_message(
    request: MessageAnalysisRequest,
    background_tasks: BackgroundTasks = None
):
    """分析消息的语义信息"""
    
    # 验证协议支持
    if request.source_protocol not in SERVICE_CONFIG["supported_protocols"]:
        raise HTTPException(status_code=400, detail=f"不支持的源协议: {request.source_protocol}")
    
    if request.target_protocol and request.target_protocol not in SERVICE_CONFIG["supported_protocols"]:
        raise HTTPException(status_code=400, detail=f"不支持的目标协议: {request.target_protocol}")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建处理结果
    result = ProcessingResult(
        task_id=task_id,
        status="processing",
        message="正在分析消息语义...",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 存储任务
    processing_tasks[task_id] = result
    
    # 异步处理
    background_tasks.add_task(
        analyze_message_async,
        task_id,
        request
    )
    
    return result

# 异步消息分析函数
async def analyze_message_async(task_id: str, request: MessageAnalysisRequest):
    """异步分析消息语义"""
    
    try:
        # 更新任务状态
        processing_tasks[task_id].status = "processing"
        processing_tasks[task_id].message = "正在解析消息结构..."
        processing_tasks[task_id].updated_at = datetime.now()
        
        # 分析消息
        analysis_result = await asyncio.get_event_loop().run_in_executor(
            None,
            semantic_analyzer.analyze_message,
            request.message,
            request.source_protocol,
            request.analysis_type
        )
        
        # 如果有目标协议，进行转换分析
        if request.target_protocol:
            processing_tasks[task_id].message = "正在分析转换可能性..."
            processing_tasks[task_id].updated_at = datetime.now()
            
            conversion_analysis = await asyncio.get_event_loop().run_in_executor(
                None,
                semantic_analyzer.analyze_conversion_feasibility,
                request.message,
                request.source_protocol,
                request.target_protocol
            )
            analysis_result["conversion_analysis"] = conversion_analysis
        
        # 更新任务结果
        processing_tasks[task_id].status = "completed"
        processing_tasks[task_id].message = "消息分析完成"
        processing_tasks[task_id].data = analysis_result
        processing_tasks[task_id].updated_at = datetime.now()
        
        logger.info(f"Message analysis completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Message analysis failed: {e}")
        
        # 更新任务状态为失败
        processing_tasks[task_id].status = "failed"
        processing_tasks[task_id].message = "消息分析失败"
        processing_tasks[task_id].error = str(e)
        processing_tasks[task_id].updated_at = datetime.now()

# 消息转换
@app.post("/convert", response_model=ProcessingResult)
async def convert_message(
    request: MessageConversionRequest,
    background_tasks: BackgroundTasks = None
):
    """转换消息格式"""
    
    # 验证协议支持
    if request.source_protocol not in SERVICE_CONFIG["supported_protocols"]:
        raise HTTPException(status_code=400, detail=f"不支持的源协议: {request.source_protocol}")
    
    if request.target_protocol not in SERVICE_CONFIG["supported_protocols"]:
        raise HTTPException(status_code=400, detail=f"不支持的目标协议: {request.target_protocol}")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建处理结果
    result = ProcessingResult(
        task_id=task_id,
        status="processing",
        message="正在转换消息格式...",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 存储任务
    processing_tasks[task_id] = result
    
    # 异步处理
    background_tasks.add_task(
        convert_message_async,
        task_id,
        request
    )
    
    return result

# 异步消息转换函数
async def convert_message_async(task_id: str, request: MessageConversionRequest):
    """异步转换消息格式"""
    
    try:
        # 更新任务状态
        processing_tasks[task_id].status = "processing"
        processing_tasks[task_id].message = "正在查找映射规则..."
        processing_tasks[task_id].updated_at = datetime.now()
        
        # 获取映射规则
        mapping_rules = request.mapping_rules
        if not mapping_rules:
            mapping_rules = await asyncio.get_event_loop().run_in_executor(
                None,
                mapping_manager.get_mapping_rules,
                request.source_protocol,
                request.target_protocol,
                request.target_message_type
            )
        
        # 转换消息
        processing_tasks[task_id].message = "正在执行消息转换..."
        processing_tasks[task_id].updated_at = datetime.now()
        
        conversion_result = await asyncio.get_event_loop().run_in_executor(
            None,
            message_converter.convert_message,
            request.source_message,
            request.source_protocol,
            request.target_protocol,
            mapping_rules,
            request.target_message_type
        )
        
        # 更新任务结果
        processing_tasks[task_id].status = "completed"
        processing_tasks[task_id].message = "消息转换完成"
        processing_tasks[task_id].data = conversion_result
        processing_tasks[task_id].updated_at = datetime.now()
        
        logger.info(f"Message conversion completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Message conversion failed: {e}")
        
        # 更新任务状态为失败
        processing_tasks[task_id].status = "failed"
        processing_tasks[task_id].message = "消息转换失败"
        processing_tasks[task_id].error = str(e)
        processing_tasks[task_id].updated_at = datetime.now()

# 语义标注
@app.post("/annotate")
async def create_semantic_annotation(request: SemanticAnnotationRequest):
    """创建语义标注"""
    
    try:
        # 执行语义标注
        annotation_result = await asyncio.get_event_loop().run_in_executor(
            None,
            semantic_analyzer.annotate_field,
            request.field_name,
            request.field_value,
            request.context,
            request.confidence_threshold
        )
        
        return {
            "success": True,
            "annotation": annotation_result,
            "confidence": annotation_result.get("confidence", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Semantic annotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"语义标注失败: {str(e)}")

# 映射规则管理
@app.post("/mappings")
async def create_mapping_rule(request: MappingRuleRequest):
    """创建映射规则"""
    
    try:
        # 创建映射规则
        rule_id = await asyncio.get_event_loop().run_in_executor(
            None,
            mapping_manager.create_mapping_rule,
            request.source_protocol,
            request.target_protocol,
            request.message_type,
            request.rules,
            request.version,
            request.description
        )
        
        return {
            "success": True,
            "rule_id": rule_id,
            "message": "映射规则创建成功"
        }
        
    except Exception as e:
        logger.error(f"Create mapping rule failed: {e}")
        raise HTTPException(status_code=500, detail=f"创建映射规则失败: {str(e)}")

# 获取映射规则
@app.get("/mappings")
async def get_mapping_rules(
    source_protocol: Optional[str] = None,
    target_protocol: Optional[str] = None,
    message_type: Optional[str] = None
):
    """获取映射规则"""
    
    try:
        rules = await asyncio.get_event_loop().run_in_executor(
            None,
            mapping_manager.get_mapping_rules,
            source_protocol,
            target_protocol,
            message_type
        )
        
        return {
            "success": True,
            "rules": rules,
            "total": len(rules)
        }
        
    except Exception as e:
        logger.error(f"Get mapping rules failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取映射规则失败: {str(e)}")

# 获取处理状态
@app.get("/tasks/{task_id}", response_model=ProcessingResult)
async def get_processing_status(task_id: str):
    """获取处理任务状态"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return processing_tasks[task_id]

# 获取处理历史
@app.get("/tasks")
async def get_processing_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """获取处理任务列表"""
    
    tasks = list(processing_tasks.values())
    
    # 按状态过滤
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    # 按时间排序
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    
    # 分页
    total = len(tasks)
    tasks = tasks[offset:offset + limit]
    
    return {
        "tasks": tasks,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# 获取支持的协议
@app.get("/protocols")
async def get_supported_protocols():
    """获取支持的协议列表"""
    return {
        "protocols": SERVICE_CONFIG["supported_protocols"],
        "total": len(SERVICE_CONFIG["supported_protocols"])
    }

# 获取语义字段
@app.get("/semantic-fields")
async def get_semantic_fields(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """获取语义字段列表"""
    
    try:
        fields = await asyncio.get_event_loop().run_in_executor(
            None,
            semantic_analyzer.get_semantic_fields,
            category,
            search
        )
        
        return {
            "success": True,
            "fields": fields,
            "total": len(fields)
        }
        
    except Exception as e:
        logger.error(f"Get semantic fields failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取语义字段失败: {str(e)}")

# 启动事件
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("Semantic Interoperability Service starting up...")
    
    # 初始化语义分析器
    await asyncio.get_event_loop().run_in_executor(
        None,
        semantic_analyzer.initialize
    )
    
    # 初始化消息转换器
    await asyncio.get_event_loop().run_in_executor(
        None,
        message_converter.initialize
    )
    
    # 初始化映射管理器
    await asyncio.get_event_loop().run_in_executor(
        None,
        mapping_manager.initialize
    )
    
    logger.info("Semantic Interoperability Service started successfully")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("Semantic Interoperability Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_CONFIG["port"])
