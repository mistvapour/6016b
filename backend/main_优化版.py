"""
优化版本的 main.py - 确保能正常启动
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os, io, csv, logging, re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库相关导入
try:
    from db import call_proc, query, exec_sql
    DB_AVAILABLE = True
    logger.info("数据库模块已加载")
except ImportError as e:
    logger.warning(f"数据库模块导入失败: {e}")
    DB_AVAILABLE = False

# API模块导入（使用 try-except 确保即使某些模块失败也能启动）
API_MODULES = {}

try:
    from pdf_api import include_pdf_routes
    API_MODULES['pdf'] = include_pdf_routes
    logger.info("PDF API模块已加载")
except ImportError as e:
    logger.warning(f"PDF API模块导入失败: {e}")
    API_MODULES['pdf'] = None

try:
    from mqtt_api import router as mqtt_router
    API_MODULES['mqtt'] = mqtt_router
    logger.info("MQTT API模块已加载")
except ImportError as e:
    logger.warning(f"MQTT API模块导入失败: {e}")
    API_MODULES['mqtt'] = None

try:
    from universal_import_api import include_universal_routes
    API_MODULES['universal'] = include_universal_routes
    logger.info("Universal API模块已加载")
except ImportError as e:
    logger.warning(f"Universal API模块导入失败: {e}")
    API_MODULES['universal'] = None

try:
    from semantic_interop_api import include_semantic_routes
    API_MODULES['semantic'] = include_semantic_routes
    logger.info("Semantic API模块已加载")
except ImportError as e:
    logger.warning(f"Semantic API模块导入失败: {e}")
    API_MODULES['semantic'] = None

try:
    from cdm_api import include_cdm_routes
    API_MODULES['cdm'] = include_cdm_routes
    logger.info("CDM API模块已加载")
except ImportError as e:
    logger.warning(f"CDM API模块导入失败: {e}")
    API_MODULES['cdm'] = None

try:
    from unified_api import include_unified_routes
    API_MODULES['unified'] = include_unified_routes
    logger.info("Unified API模块已加载")
except ImportError as e:
    logger.warning(f"Unified API模块导入失败: {e}")
    API_MODULES['unified'] = None

try:
    from message_generation_api import include_message_generation_routes
    API_MODULES['message_generation'] = include_message_generation_routes
    logger.info("消息生成API模块已加载")
except ImportError as e:
    logger.warning(f"消息生成API模块导入失败: {e}")
    API_MODULES['message_generation'] = None

# 创建FastAPI应用
app = FastAPI(
    title="MIL-STD-6016 Mini API", 
    version="0.6.0",
    description="军事标准6016数据分析和处理API"
)

# CORS配置 - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 健康检查 ----------
@app.get("/")
def root():
    """根路径"""
    return {
        "name": "MIL-STD-6016 API",
        "version": "0.6.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
def health():
    """健康检查端点"""
    try:
        if DB_AVAILABLE:
            try:
                row = query("SELECT DATABASE() AS db, VERSION() AS version")[0]
                return {"ok": True, "database": "connected", **row}
            except Exception as e:
                return {"ok": True, "database": "available_but_error", "error": str(e)}
        else:
            return {"ok": True, "database": "not_available", "message": "数据库模块未加载"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"ok": True, "error": str(e)}

# ---------- 注册API模块 ----------
def register_api_modules():
    """注册所有可用的API模块"""
    if API_MODULES.get('pdf'):
        try:
            API_MODULES['pdf'](app)
            logger.info("✓ PDF API路由已注册")
        except Exception as e:
            logger.error(f"注册PDF API路由失败: {e}")

    if API_MODULES.get('mqtt'):
        try:
            app.include_router(API_MODULES['mqtt'])
            logger.info("✓ MQTT API路由已注册")
        except Exception as e:
            logger.error(f"注册MQTT API路由失败: {e}")

    if API_MODULES.get('universal'):
        try:
            API_MODULES['universal'](app)
            logger.info("✓ Universal API路由已注册")
        except Exception as e:
            logger.error(f"注册Universal API路由失败: {e}")

    if API_MODULES.get('semantic'):
        try:
            API_MODULES['semantic'](app)
            logger.info("✓ Semantic API路由已注册")
        except Exception as e:
            logger.error(f"注册Semantic API路由失败: {e}")

    if API_MODULES.get('cdm'):
        try:
            API_MODULES['cdm'](app)
            logger.info("✓ CDM API路由已注册")
        except Exception as e:
            logger.error(f"注册CDM API路由失败: {e}")

    if API_MODULES.get('unified'):
        try:
            API_MODULES['unified'](app)
            logger.info("✓ Unified API路由已注册")
        except Exception as e:
            logger.error(f"注册Unified API路由失败: {e}")

    if API_MODULES.get('message_generation'):
        try:
            API_MODULES['message_generation'](app)
            logger.info("✓ 消息生成API路由已注册")
        except Exception as e:
            logger.error(f"注册消息生成API路由失败: {e}")

# 注册所有API模块
register_api_modules()

# 从原 main.py 复制其他路由（搜索、比较等）
# ... 这里需要从原文件复制所有路由定义 ...

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动 MIL-STD-6016 API 服务器")
    print("=" * 60)
    print(f"📊 数据库状态: {'可用' if DB_AVAILABLE else '不可用'}")
    print(f"📡 已加载模块数: {sum(1 for v in API_MODULES.values() if v)}/{len(API_MODULES)}")
    print("=" * 60)
    print("🌐 服务地址: http://127.0.0.1:8000")
    print("📚 API文档: http://127.0.0.1:8000/docs")
    print("❤️  健康检查: http://127.0.0.1:8000/api/health")
    print("=" * 60)
    print()
    
    # Windows 下禁用 reload 以避免 Segmentation fault
    import os
    is_windows = os.name == 'nt'
    reload_enabled = not is_windows
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        reload=reload_enabled,
        log_level="info"
    )

