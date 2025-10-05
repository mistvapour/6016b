# backend/mqtt_api.py
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import tempfile
import logging
from pathlib import Path
from typing import Optional

from mqtt_adapter.extract_tables import extract_mqtt_tables
from mqtt_adapter.parse_sections import analyze_mqtt_structure
from mqtt_adapter.build_sim import build_sim, validate_sim
from mqtt_adapter.export_yaml import export_mqtt_complete, validate_yaml_output

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mqtt", tags=["mqtt"])

@router.post("/pdf_to_yaml")
async def pdf_to_yaml(
    file: UploadFile = File(...), 
    pages: str = Query("10-130", description="页面范围，例如: 10-130 或 10-20,25-30"),
    output_dir: Optional[str] = Query("mqtt_output", description="输出目录")
):
    """
    MQTT PDF转YAML的主要接口
    
    Args:
        file: 上传的PDF文件
        pages: 页面范围字符串
        output_dir: 输出目录
    
    Returns:
        处理结果和生成的YAML文件信息
    """
    temp_pdf = None
    
    try:
        logger.info(f"Starting MQTT PDF processing: {file.filename}")
        
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # 保存上传的文件到临时位置
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_pdf = tmp.name
        
        logger.info(f"Saved uploaded file to {temp_pdf}")
        
        # 1. 分析文档结构
        logger.info("Step 1: Analyzing document structure...")
        sections, page_texts = analyze_mqtt_structure(temp_pdf, pages)
        
        if not sections:
            raise HTTPException(status_code=400, detail="No MQTT control packet sections found in the specified pages")
        
        logger.info(f"Found {len(sections)} MQTT sections")
        
        # 2. 提取表格
        logger.info("Step 2: Extracting tables...")
        best_tables, page_list = extract_mqtt_tables(temp_pdf, pages)
        
        if not best_tables:
            raise HTTPException(status_code=400, detail="No suitable tables found in the specified pages")
        
        logger.info(f"Extracted {len(best_tables)} tables from {len(page_list)} pages")
        
        # 3. 构建SIM
        logger.info("Step 3: Building SIM...")
        sim = build_sim(sections, best_tables, page_texts)
        
        # 4. 验证SIM
        logger.info("Step 4: Validating SIM...")
        validation_issues = validate_sim(sim)
        
        if validation_issues:
            logger.warning(f"SIM validation found {len(validation_issues)} issues")
            for issue in validation_issues[:5]:  # 只记录前5个问题
                logger.warning(f"  - {issue}")
        
        # 5. 导出YAML
        logger.info("Step 5: Exporting YAML...")
        export_result = export_mqtt_complete(sim, output_dir)
        
        if not export_result['success']:
            raise HTTPException(status_code=500, detail=f"YAML export failed: {export_result['error']}")
        
        # 6. 验证输出
        logger.info("Step 6: Validating YAML output...")
        yaml_validation = validate_yaml_output(export_result['main_yaml'])
        
        # 构建响应
        response = {
            "success": True,
            "message": f"Successfully processed MQTT PDF with {len(sections)} control packets",
            "data": {
                "pdf_filename": file.filename,
                "pages_processed": len(page_list),
                "sections_found": len(sections),
                "tables_extracted": len(best_tables),
                "messages_created": len(sim.get('spec_messages', [])),
                "total_fields": sim.get('metadata', {}).get('total_fields', 0),
                "output_dir": export_result['output_dir'],
                "files": export_result['files'],
                "main_yaml": export_result['main_yaml'],
                "main_json": export_result['main_json'],
                "manifest": export_result.get('manifest'),
                "validation": {
                    "sim_issues": validation_issues,
                    "yaml_validation": yaml_validation
                },
                "sections": [
                    {
                        "label": s["label"],
                        "pages": s["pages"],
                        "subsections": s.get("subsections", [])
                    }
                    for s in sections
                ]
            }
        }
        
        logger.info(f"MQTT PDF processing completed successfully: {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MQTT PDF processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        # 清理临时文件
        if temp_pdf and Path(temp_pdf).exists():
            try:
                Path(temp_pdf).unlink()
                logger.debug(f"Cleaned up temporary file: {temp_pdf}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_pdf}: {e}")

@router.get("/download/{filename}")
async def download_file(filename: str, output_dir: str = Query("mqtt_output")):
    """下载生成的YAML文件"""
    try:
        file_path = Path(output_dir) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list_outputs")
async def list_output_files(output_dir: str = Query("mqtt_output")):
    """列出输出目录中的文件"""
    try:
        output_path = Path(output_dir)
        
        if not output_path.exists():
            return {"files": [], "output_dir": str(output_path)}
        
        files = []
        for file_path in output_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(output_path)
                files.append({
                    "name": file_path.name,
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "type": file_path.suffix.lower()
                })
        
        return {
            "files": files,
            "output_dir": str(output_path),
            "total_files": len(files)
        }
    
    except Exception as e:
        logger.error(f"List files failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate_yaml")
async def validate_yaml_file(yaml_path: str = Query(..., description="YAML文件路径")):
    """验证YAML文件格式"""
    try:
        if not Path(yaml_path).exists():
            raise HTTPException(status_code=404, detail="YAML file not found")
        
        validation_result = validate_yaml_output(yaml_path)
        
        return {
            "success": True,
            "validation": validation_result,
            "file_path": yaml_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YAML validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """MQTT处理模块健康检查"""
    try:
        # 检查依赖模块
        import camelot
        import pdfplumber
        import yaml
        import pandas as pd
        
        return {
            "status": "healthy",
            "service": "MQTT PDF Processor",
            "dependencies": {
                "camelot": True,
                "pdfplumber": True, 
                "yaml": True,
                "pandas": True
            }
        }
    except ImportError as e:
        return {
            "status": "unhealthy",
            "error": f"Missing dependency: {e}",
            "service": "MQTT PDF Processor"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 一键完整流水线接口
@router.post("/complete_pipeline")
async def complete_pipeline(
    file: UploadFile = File(...),
    pages: str = Query("10-130"),
    output_dir: str = Query("mqtt_output"),
    import_to_db: bool = Query(False, description="是否直接导入到数据库"),
    dry_run: bool = Query(True, description="数据库导入是否为试运行")
):
    """
    完整的PDF→YAML→数据库流水线
    """
    try:
        # 第一步：PDF转YAML
        yaml_result = await pdf_to_yaml(file, pages, output_dir)
        
        if not yaml_result["success"]:
            return yaml_result
        
        result = {
            "pdf_processing": yaml_result,
            "database_import": None
        }
        
        # 第二步：导入数据库（如果需要）
        if import_to_db:
            logger.info("Step 7: Importing to database...")
            
            try:
                import requests
                
                # 构建导入请求
                yaml_files = yaml_result["data"]["files"]
                main_yaml = yaml_result["data"]["main_yaml"]
                
                # 调用现有的导入API
                import_response = requests.post(
                    "http://localhost:8000/api/import/yaml",
                    params={
                        "yaml_path": main_yaml,
                        "dry_run": dry_run
                    },
                    timeout=60
                )
                
                if import_response.status_code == 200:
                    import_result = import_response.json()
                    result["database_import"] = import_result
                    logger.info(f"Database import {'(dry run) ' if dry_run else ''}completed successfully")
                else:
                    error_msg = f"Database import failed: HTTP {import_response.status_code}"
                    logger.error(error_msg)
                    result["database_import"] = {
                        "success": False,
                        "error": error_msg
                    }
                    
            except Exception as e:
                error_msg = f"Database import failed: {e}"
                logger.error(error_msg)
                result["database_import"] = {
                    "success": False,
                    "error": error_msg
                }
        
        # 设置整体成功状态
        overall_success = yaml_result["success"]
        if import_to_db and result["database_import"]:
            overall_success = overall_success and result["database_import"].get("success", False)
        
        result["success"] = overall_success
        result["message"] = f"Pipeline completed: PDF processed, {'database import ' + ('(dry run) ' if dry_run else '') + ('succeeded' if result.get('database_import', {}).get('success') else 'failed') if import_to_db else 'YAML generated'}"
        
        return result
        
    except Exception as e:
        logger.error(f"Complete pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
