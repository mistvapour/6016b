#!/usr/bin/env python3
"""
PDF处理微服务
专门负责PDF文档的解析、处理和转换
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import logging
import tempfile
import os
import json
from datetime import datetime
import uuid

# 导入PDF处理模块
import sys
sys.path.append('/app')
from pdf_processor import PDFProcessor
from validators import DataValidator

# 配置
SERVICE_CONFIG = {
    "name": "pdf-service",
    "version": "1.0.0",
    "port": 8001,
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "supported_formats": ["pdf"],
    "processing_timeout": 300  # 5分钟
}

# 创建FastAPI应用
app = FastAPI(
    title="PDF Processing Service",
    version=SERVICE_CONFIG["version"],
    description="MIL-STD-6016 PDF文档处理微服务"
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
class ProcessingRequest(BaseModel):
    standard: str = "MIL-STD-6016"
    edition: str = "B"
    output_format: str = "yaml"
    enable_validation: bool = True
    enable_annotation: bool = True

class ProcessingResult(BaseModel):
    task_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BatchProcessingRequest(BaseModel):
    files: List[str]  # 文件路径列表
    standard: str = "MIL-STD-6016"
    edition: str = "B"
    output_dir: str = "/tmp/batch_output"

# 全局变量
processing_tasks: Dict[str, ProcessingResult] = {}
pdf_processor = PDFProcessor()
validator = DataValidator()

# 健康检查
@app.get("/health")
async def health_check():
    """服务健康检查"""
    return {
        "service": SERVICE_CONFIG["name"],
        "status": "healthy",
        "version": SERVICE_CONFIG["version"],
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

# 服务信息
@app.get("/info")
async def service_info():
    """获取服务信息"""
    return {
        "name": SERVICE_CONFIG["name"],
        "version": SERVICE_CONFIG["version"],
        "supported_formats": SERVICE_CONFIG["supported_formats"],
        "max_file_size": SERVICE_CONFIG["max_file_size"],
        "processing_timeout": SERVICE_CONFIG["processing_timeout"]
    }

# 单文件PDF处理
@app.post("/process", response_model=ProcessingResult)
async def process_pdf(
    file: UploadFile = File(...),
    standard: str = Form("MIL-STD-6016"),
    edition: str = Form("B"),
    output_format: str = Form("yaml"),
    enable_validation: bool = Form(True),
    enable_annotation: bool = Form(True),
    background_tasks: BackgroundTasks = None
):
    """处理单个PDF文件"""
    
    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 验证文件大小
    if file.size > SERVICE_CONFIG["max_file_size"]:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建处理结果
    result = ProcessingResult(
        task_id=task_id,
        status="processing",
        message="PDF处理中...",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 存储任务
    processing_tasks[task_id] = result
    
    # 异步处理
    background_tasks.add_task(
        process_pdf_async,
        task_id,
        file,
        standard,
        edition,
        output_format,
        enable_validation,
        enable_annotation
    )
    
    return result

# 异步PDF处理函数
async def process_pdf_async(
    task_id: str,
    file: UploadFile,
    standard: str,
    edition: str,
    output_format: str,
    enable_validation: bool,
    enable_annotation: bool
):
    """异步处理PDF文件"""
    
    try:
        # 更新任务状态
        processing_tasks[task_id].status = "processing"
        processing_tasks[task_id].message = "正在解析PDF文件..."
        processing_tasks[task_id].updated_at = datetime.now()
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 处理PDF
            logger.info(f"Processing PDF: {file.filename}")
            
            # 使用PDF处理器
            result_data = await asyncio.get_event_loop().run_in_executor(
                None,
                pdf_processor.process_pdf,
                tmp_file_path,
                standard,
                edition
            )
            
            # 验证数据
            if enable_validation:
                processing_tasks[task_id].message = "正在验证数据..."
                processing_tasks[task_id].updated_at = datetime.now()
                
                validation_result = validator.validate_sim_data(result_data)
                result_data["validation_result"] = validation_result
            
            # 生成输出文件
            output_files = []
            if output_format == "yaml":
                yaml_file = f"/tmp/output_{task_id}.yaml"
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    pdf_processor.export_to_yaml,
                    result_data,
                    yaml_file
                )
                output_files.append(yaml_file)
            
            # 更新任务结果
            processing_tasks[task_id].status = "completed"
            processing_tasks[task_id].message = "PDF处理完成"
            processing_tasks[task_id].data = {
                "result": result_data,
                "output_files": output_files,
                "processing_time": (datetime.now() - processing_tasks[task_id].created_at).total_seconds()
            }
            processing_tasks[task_id].updated_at = datetime.now()
            
            logger.info(f"PDF processing completed: {task_id}")
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        
        # 更新任务状态为失败
        processing_tasks[task_id].status = "failed"
        processing_tasks[task_id].message = "PDF处理失败"
        processing_tasks[task_id].error = str(e)
        processing_tasks[task_id].updated_at = datetime.now()

# 获取处理状态
@app.get("/tasks/{task_id}", response_model=ProcessingResult)
async def get_processing_status(task_id: str):
    """获取处理任务状态"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return processing_tasks[task_id]

# 批量处理
@app.post("/batch-process")
async def batch_process_pdfs(request: BatchProcessingRequest):
    """批量处理PDF文件"""
    
    batch_id = str(uuid.uuid4())
    results = []
    
    for file_path in request.files:
        if not os.path.exists(file_path):
            results.append({
                "file": file_path,
                "status": "error",
                "message": "文件不存在"
            })
            continue
        
        try:
            # 处理单个文件
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                pdf_processor.process_pdf,
                file_path,
                request.standard,
                request.edition
            )
            
            results.append({
                "file": file_path,
                "status": "success",
                "result": result
            })
            
        except Exception as e:
            results.append({
                "file": file_path,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "batch_id": batch_id,
        "total_files": len(request.files),
        "success_count": len([r for r in results if r["status"] == "success"]),
        "error_count": len([r for r in results if r["status"] == "error"]),
        "results": results
    }

# 获取支持的标准
@app.get("/standards")
async def get_supported_standards():
    """获取支持的PDF标准"""
    return {
        "standards": [
            {
                "name": "MIL-STD-6016",
                "description": "美军标准6016 - 战术数据链消息标准",
                "editions": ["A", "B", "C"],
                "supported": True
            },
            {
                "name": "MIL-STD-3011",
                "description": "美军标准3011 - 联合战术信息分发系统",
                "editions": ["A", "B"],
                "supported": True
            },
            {
                "name": "STANAG-5516",
                "description": "北约标准5516 - 战术数据交换",
                "editions": ["1", "2", "3"],
                "supported": True
            }
        ]
    }

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

# 删除任务
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除处理任务"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del processing_tasks[task_id]
    return {"message": "任务已删除"}

# 清理过期任务
@app.post("/cleanup")
async def cleanup_expired_tasks():
    """清理过期任务"""
    current_time = datetime.now()
    expired_tasks = []
    
    for task_id, task in processing_tasks.items():
        # 清理超过1小时的已完成或失败任务
        if (task.status in ["completed", "failed"] and 
            (current_time - task.updated_at).total_seconds() > 3600):
            expired_tasks.append(task_id)
    
    for task_id in expired_tasks:
        del processing_tasks[task_id]
    
    return {
        "message": f"清理了 {len(expired_tasks)} 个过期任务",
        "cleaned_tasks": expired_tasks
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("PDF Processing Service starting up...")
    
    # 创建输出目录
    os.makedirs("/tmp/pdf_output", exist_ok=True)
    os.makedirs("/tmp/batch_output", exist_ok=True)
    
    logger.info("PDF Processing Service started successfully")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("PDF Processing Service shutting down...")
    
    # 清理临时文件
    import shutil
    if os.path.exists("/tmp/pdf_output"):
        shutil.rmtree("/tmp/pdf_output")
    if os.path.exists("/tmp/batch_output"):
        shutil.rmtree("/tmp/batch_output")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_CONFIG["port"])
