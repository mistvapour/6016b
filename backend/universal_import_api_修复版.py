#!/usr/bin/env python3
"""
统一多格式导入API接口
为统一导入系统提供FastAPI接口
修复版：延迟初始化，避免导入时阻塞
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

# ==========================================
# 延迟初始化：避免导入时阻塞
# ==========================================
_universal_system = None

def get_universal_system():
    """获取统一导入系统实例（延迟初始化）"""
    global _universal_system
    if _universal_system is None:
        logger.info("初始化 UniversalImportSystem...")
        _universal_system = UniversalImportSystem()
        logger.info("UniversalImportSystem 初始化完成")
    return _universal_system

@router.get("/status")
async def get_system_status():
    """获取统一导入系统状态"""
    try:
        status = get_universal_system().get_system_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的文件格式列表"""
    try:
        formats = get_universal_system().get_supported_formats()
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
    temp_path = None
    try:
        # 保存上传的文件到临时位置
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
        
        # 检测格式
        format_info = get_universal_system().detect_file_format(temp_path)
        adapter = get_universal_system().find_adapter(temp_path, format_info["mime_type"])
        
        if adapter:
            standard_info = adapter.detect_standard(temp_path)
            return {
                "success": True,
                "format_info": format_info,
                "standard_info": standard_info,
                "adapter_available": True,
                "supported_formats": get_universal_system().get_supported_formats()
            }
        else:
            return {
                "success": False,
                "format_info": format_info,
                "adapter_available": False,
                "supported_formats": get_universal_system().get_supported_formats()
            }
    except Exception as e:
        logger.error(f"格式检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

# ... 其他路由也需要修改为使用 get_universal_system() ...

