#!/usr/bin/env python3
"""
统一多格式导入API接口
为统一导入系统提供FastAPI接口
"""
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
from pathlib import Path
import logging
import json

from universal_import_system import UniversalImportSystem

router = APIRouter(prefix="/api/universal", tags=["universal_import"])
logger = logging.getLogger(__name__)

# 初始化统一导入系统
universal_system = UniversalImportSystem()

@router.get("/status")
async def get_system_status():
    """获取统一导入系统状态"""
    try:
        status = universal_system.get_system_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的文件格式列表"""
    try:
        formats = universal_system.get_supported_formats()
        return {
            "success": True,
            "supported_formats": formats,
            "total_adapters": len(formats)
        }
    except Exception as e:
        logger.error(f"获取支持格式失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-format")
async def detect_file_format(file: UploadFile = File(...)):
    """检测上传文件的格式和标准类型"""
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        try:
            # 检测文件格式
            format_info = universal_system.detect_file_format(temp_path)
            
            # 查找适配器
            adapter = universal_system.find_adapter(temp_path, format_info["mime_type"])
            
            if adapter:
                # 检测标准类型
                standard_info = adapter.detect_standard(temp_path)
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "format_info": format_info,
                    "standard_info": standard_info,
                    "adapter": adapter.__class__.__name__,
                    "supported": True
                }
            else:
                return {
                    "success": True,
                    "filename": file.filename,
                    "format_info": format_info,
                    "supported": False,
                    "message": f"不支持的文件格式: {format_info.get('mime_type', 'unknown')}",
                    "supported_formats": universal_system.get_supported_formats()
                }
                
        finally:
            # 清理临时文件
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"文件格式检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-file")
async def process_single_file(
    file: UploadFile = File(...),
    output_dir: Optional[str] = Form(None),
    pages: Optional[str] = Form("1-100"),
    standard: Optional[str] = Form(None),
    version: Optional[str] = Form(None)
):
    """处理单个文件"""
    try:
        # 设置输出目录
        if not output_dir:
            output_dir = f"universal_output/{Path(file.filename).stem}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存上传的文件
        file_path = os.path.join(output_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # 准备处理参数
        kwargs = {
            "output_dir": output_dir,
            "pages": pages,
            "standard": standard,
            "version": version
        }
        
        # 处理文件
        result = universal_system.process_file(file_path, **kwargs)
        
        return {
            "success": result["success"],
            "result": result,
            "file_saved_to": file_path
        }
        
    except Exception as e:
        logger.error(f"文件处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-batch")
async def process_batch_files(
    files: List[UploadFile] = File(...),
    output_dir: Optional[str] = Form(None),
    pages: Optional[str] = Form("1-100"),
    standard: Optional[str] = Form(None),
    version: Optional[str] = Form(None)
):
    """批量处理多个文件"""
    try:
        # 设置输出目录
        if not output_dir:
            output_dir = "universal_output/batch_processing"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存所有上传的文件
        file_paths = []
        for file in files:
            file_path = os.path.join(output_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(file_path)
        
        # 准备处理参数
        kwargs = {
            "output_dir": output_dir,
            "pages": pages,
            "standard": standard,
            "version": version
        }
        
        # 批量处理
        result = universal_system.process_files(file_paths, **kwargs)
        
        return {
            "success": result["success"],
            "files_processed": len(file_paths),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete-pipeline")
async def complete_import_pipeline(
    files: List[UploadFile] = File(...),
    import_to_db: bool = Form(False),
    dry_run: bool = Form(True),
    output_dir: Optional[str] = Form(None),
    pages: Optional[str] = Form("1-100"),
    standard: Optional[str] = Form(None),
    version: Optional[str] = Form(None)
):
    """完整的导入流水线：文件处理 -> YAML生成 -> 数据库导入"""
    try:
        # 设置输出目录
        if not output_dir:
            output_dir = "universal_output/complete_pipeline"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存所有上传的文件
        file_paths = []
        for file in files:
            file_path = os.path.join(output_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(file_path)
        
        # 准备处理参数
        kwargs = {
            "output_dir": output_dir,
            "pages": pages,
            "standard": standard,
            "version": version
        }
        
        # 执行完整流水线
        result = universal_system.complete_pipeline(
            file_paths, 
            import_to_db=import_to_db,
            dry_run=dry_run,
            **kwargs
        )
        
        return {
            "success": result["success"],
            "pipeline_stage": result.get("stage", "complete"),
            "files_processed": len(file_paths),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"完整流水线执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-yaml")
async def import_yaml_files(
    yaml_paths: List[str] = Query(..., description="YAML文件路径列表"),
    dry_run: bool = Query(True, description="是否为试运行")
):
    """导入YAML文件到数据库"""
    try:
        result = universal_system.import_to_database(yaml_paths, dry_run)
        return {
            "success": result["success"],
            "result": result
        }
    except Exception as e:
        logger.error(f"YAML导入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-directory")
async def process_directory(
    directory_path: str = Query(..., description="目录路径"),
    file_pattern: Optional[str] = Query("*", description="文件匹配模式"),
    import_to_db: bool = Query(False, description="是否导入数据库"),
    dry_run: bool = Query(True, description="数据库导入是否为试运行"),
    output_dir: Optional[str] = Query(None, description="输出目录")
):
    """处理目录中的所有匹配文件"""
    try:
        # 检查目录是否存在
        if not os.path.isdir(directory_path):
            raise HTTPException(status_code=404, detail=f"目录不存在: {directory_path}")
        
        # 查找匹配的文件
        from glob import glob
        pattern = os.path.join(directory_path, file_pattern)
        file_paths = glob(pattern)
        
        if not file_paths:
            return {
                "success": False,
                "message": f"在目录 {directory_path} 中未找到匹配模式 {file_pattern} 的文件",
                "pattern": pattern
            }
        
        # 设置输出目录
        if not output_dir:
            output_dir = f"universal_output/directory_{Path(directory_path).name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 执行完整流水线
        result = universal_system.complete_pipeline(
            file_paths,
            import_to_db=import_to_db,
            dry_run=dry_run,
            output_dir=output_dir
        )
        
        return {
            "success": result["success"],
            "directory_processed": directory_path,
            "files_found": len(file_paths),
            "file_list": [os.path.basename(f) for f in file_paths],
            "result": result
        }
        
    except Exception as e:
        logger.error(f"目录处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processing-history")
async def get_processing_history(
    limit: int = Query(10, description="返回记录数限制"),
    format_filter: Optional[str] = Query(None, description="按格式过滤"),
    standard_filter: Optional[str] = Query(None, description="按标准过滤")
):
    """获取处理历史记录（示例接口）"""
    try:
        # 这里应该从数据库或日志文件中获取历史记录
        # 当前返回示例数据
        history = [
            {
                "id": 1,
                "timestamp": "2024-10-02T17:30:00",
                "files_processed": 3,
                "formats": ["PDF", "XML", "JSON"],
                "standards": ["MIL-STD-6016", "MAVLink", "Generic"],
                "success": True,
                "processing_time": "45.2 seconds"
            },
            {
                "id": 2,
                "timestamp": "2024-10-02T16:15:00",
                "files_processed": 1,
                "formats": ["PDF"],
                "standards": ["MQTT"],
                "success": True,
                "processing_time": "12.8 seconds"
            }
        ]
        
        # 应用过滤器
        if format_filter:
            history = [h for h in history if format_filter in h["formats"]]
        if standard_filter:
            history = [h for h in history if standard_filter in h["standards"]]
        
        return {
            "success": True,
            "history": history[:limit],
            "total_records": len(history)
        }
        
    except Exception as e:
        logger.error(f"获取处理历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup-temp")
async def cleanup_temp_files(
    older_than_hours: int = Query(24, description="清理多少小时前的临时文件")
):
    """清理临时文件"""
    try:
        import time
        
        temp_dirs = [
            "universal_output",
            "/tmp/pdf_processing",
            "/tmp/mqtt_processing",
            "mavlink_output",
            "json_output", 
            "csv_output",
            "xml_output"
        ]
        
        cleaned_files = 0
        cleaned_size = 0
        
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            if os.path.getmtime(file_path) < cutoff_time:
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                cleaned_files += 1
                                cleaned_size += file_size
                        except OSError:
                            continue
        
        return {
            "success": True,
            "cleaned_files": cleaned_files,
            "cleaned_size_mb": round(cleaned_size / (1024 * 1024), 2),
            "cutoff_hours": older_than_hours
        }
        
    except Exception as e:
        logger.error(f"清理临时文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 为了与现有API保持兼容，添加一些便捷的别名接口

@router.post("/pdf/auto-process")
async def auto_process_pdf(
    file: UploadFile = File(...),
    import_to_db: bool = Form(False),
    dry_run: bool = Form(True)
):
    """自动检测并处理PDF文件（智能路由）"""
    try:
        # 使用统一系统自动处理
        result = await complete_import_pipeline(
            files=[file],
            import_to_db=import_to_db,
            dry_run=dry_run
        )
        
        return result
        
    except Exception as e:
        logger.error(f"自动PDF处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/xml/auto-process")
async def auto_process_xml(
    file: UploadFile = File(...),
    import_to_db: bool = Form(False),
    dry_run: bool = Form(True)
):
    """自动检测并处理XML文件（智能路由）"""
    try:
        # 使用统一系统自动处理
        result = await complete_import_pipeline(
            files=[file],
            import_to_db=import_to_db,
            dry_run=dry_run
        )
        
        return result
        
    except Exception as e:
        logger.error(f"自动XML处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        status = universal_system.get_system_status()
        return {
            "status": "ok",
            "message": "统一多格式导入系统运行正常",
            "system_status": status
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# 导入路由到主应用的函数
def include_universal_routes(app):
    """将统一导入路由添加到FastAPI应用"""
    app.include_router(router)
    logger.info("统一多格式导入API路由已加载")
