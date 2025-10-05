"""
PDF处理API接口
集成PDF处理功能到FastAPI应用
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import tempfile
import logging
from pathlib import Path
import json

from pdf_adapter.pdf_processor import PDFProcessor, process_pdf_file, batch_process_pdfs

logger = logging.getLogger(__name__)

# 创建PDF处理API
pdf_app = FastAPI(title="PDF Processing API", version="1.0.0")

# CORS配置
pdf_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class PDFProcessRequest(BaseModel):
    standard: str = "MIL-STD-6016"
    edition: str = "B"
    output_dir: Optional[str] = None

class BatchProcessRequest(BaseModel):
    pdf_dir: str
    output_dir: Optional[str] = None
    standard: str = "MIL-STD-6016"
    edition: str = "B"

class ValidationRequest(BaseModel):
    sim_data: Dict[str, Any]

# 响应模型
class ProcessingResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@pdf_app.post("/api/pdf/process", response_model=ProcessingResult)
async def process_pdf(
    file: UploadFile = File(...),
    standard: str = Form("MIL-STD-6016"),
    edition: str = Form("B"),
    output_dir: Optional[str] = Form(None)
):
    """
    处理单个PDF文件
    """
    try:
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 处理PDF
            processor = PDFProcessor(standard, edition)
            result = processor.process_pdf(temp_file_path, output_dir)
            
            if result['success']:
                return ProcessingResult(
                    success=True,
                    message="PDF processed successfully",
                    data=result
                )
            else:
                return ProcessingResult(
                    success=False,
                    message="PDF processing failed",
                    error=result.get('error', 'Unknown error')
                )
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@pdf_app.post("/api/pdf/batch-process", response_model=ProcessingResult)
async def batch_process_pdfs_endpoint(request: BatchProcessRequest):
    """
    批量处理PDF文件
    """
    try:
        results = batch_process_pdfs(
            request.pdf_dir,
            request.output_dir,
            request.standard,
            request.edition
        )
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        return ProcessingResult(
            success=True,
            message=f"Batch processing completed: {success_count}/{total_count} files processed successfully",
            data={
                'results': results,
                'summary': {
                    'total': total_count,
                    'successful': success_count,
                    'failed': total_count - success_count
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@pdf_app.post("/api/pdf/validate", response_model=ProcessingResult)
async def validate_sim_data(request: ValidationRequest):
    """
    验证SIM数据
    """
    try:
        from pdf_adapter.validators import validate_pdf_extraction, generate_validation_report
        
        validation_result = validate_pdf_extraction(request.sim_data)
        
        return ProcessingResult(
            success=validation_result.valid,
            message="Validation completed",
            data={
                'valid': validation_result.valid,
                'errors': [e.__dict__ for e in validation_result.errors],
                'warnings': [w.__dict__ for w in validation_result.warnings],
                'coverage': validation_result.coverage,
                'confidence': validation_result.confidence,
                'report': generate_validation_report(validation_result)
            }
        )
    
    except Exception as e:
        logger.error(f"Error validating SIM data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@pdf_app.get("/api/pdf/status/{task_id}")
async def get_processing_status(task_id: str):
    """
    获取处理状态（用于异步处理）
    """
    # 这里可以实现任务状态查询
    # 暂时返回简单的状态信息
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Processing completed"
    }

@pdf_app.get("/api/pdf/download/{filename}")
async def download_file(filename: str):
    """
    下载生成的文件
    """
    try:
        # 这里应该根据实际的文件存储位置来构建文件路径
        file_path = Path("output") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
    
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@pdf_app.get("/api/pdf/list-outputs")
async def list_output_files(output_dir: Optional[str] = Query(None)):
    """
    列出输出文件
    """
    try:
        if output_dir is None:
            output_dir = "output"
        
        output_path = Path(output_dir)
        if not output_path.exists():
            return {"files": []}
        
        files = []
        for file_path in output_path.iterdir():
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        return {"files": files}
    
    except Exception as e:
        logger.error(f"Error listing output files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@pdf_app.get("/api/pdf/health")
async def health_check():
    """
    健康检查
    """
    return {
        "status": "healthy",
        "service": "PDF Processing API",
        "version": "1.0.0"
    }

# 将PDF API集成到主应用
def include_pdf_routes(app: FastAPI):
    """将PDF路由包含到主应用中"""
    app.include_router(pdf_app, prefix="", tags=["PDF Processing"])
