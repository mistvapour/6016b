"""
main.py 的无数据库版本 - 用于诊断数据库连接问题
完全注释掉数据库相关代码，确保服务能快速启动
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os, io, csv, logging, re

# ========== 数据库相关导入 - 已注释 ==========
# try:
#     from db import call_proc, query, exec_sql
#     DB_AVAILABLE = True
# except ImportError as e:
#     print(f"数据库模块导入失败: {e}")
#     DB_AVAILABLE = False
DB_AVAILABLE = False  # 强制禁用数据库

# API模块导入 - 保留，但如果它们依赖数据库可能会有问题
try:
    from pdf_api import include_pdf_routes
    PDF_API_AVAILABLE = True
except ImportError as e:
    print(f"PDF API模块导入失败: {e}")
    PDF_API_AVAILABLE = False

try:
    from mqtt_api import router as mqtt_router
    MQTT_API_AVAILABLE = True
except ImportError as e:
    print(f"MQTT API模块导入失败: {e}")
    MQTT_API_AVAILABLE = False

try:
    from universal_import_api import include_universal_routes
    UNIVERSAL_API_AVAILABLE = True
except ImportError as e:
    print(f"Universal API模块导入失败: {e}")
    UNIVERSAL_API_AVAILABLE = False

try:
    from semantic_interop_api import include_semantic_routes
    SEMANTIC_API_AVAILABLE = True
except ImportError as e:
    print(f"Semantic API模块导入失败: {e}")
    SEMANTIC_API_AVAILABLE = False

try:
    from cdm_api import include_cdm_routes
    CDM_API_AVAILABLE = True
except ImportError as e:
    print(f"CDM API模块导入失败: {e}")
    CDM_API_AVAILABLE = False

try:
    from unified_api import include_unified_routes
    UNIFIED_API_AVAILABLE = True
except ImportError as e:
    print(f"Unified API模块导入失败: {e}")
    UNIFIED_API_AVAILABLE = False

try:
    from message_generation_api import include_message_generation_routes
    MESSAGE_GENERATION_API_AVAILABLE = True
except ImportError as e:
    print(f"消息生成API模块导入失败: {e}")
    MESSAGE_GENERATION_API_AVAILABLE = False

# 创建FastAPI应用
app = FastAPI(
    title="MIL-STD-6016 Mini API (无数据库版)", 
    version="0.6.0-no-db",
    description="无数据库版本 - 用于诊断数据库连接问题"
)

# CORS配置
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")

# ---------- 根路径 ----------
@app.get("/")
def root():
    """根路径"""
    return {
        "name": "MIL-STD-6016 Mini API (无数据库版)",
        "version": "0.6.0-no-db",
        "status": "running",
        "database": "disabled",
        "message": "这是无数据库版本，用于诊断问题",
        "docs": "/docs",
        "health": "/api/health"
    }

# ---------- 数据模型 ----------
class BindFieldBody(BaseModel):
    concept: str
    field_id: int
    confidence: Optional[float] = 0.95
    notes: Optional[str] = None

class BindFieldToDI(BaseModel):
    field_id: int
    data_item_id: int
    confidence: Optional[float] = 0.95
    notes: Optional[str] = None

# ---------- 工具函数 ----------
_norm_re_non = re.compile(r"[^A-Z0-9]+")
_norm_re_spc = re.compile(r"\s+")

def normalize_canonical(s: str) -> str:
    """规范化名字：大写→去非字母数字→压空格"""
    if s is None:
        return ""
    t = s.upper()
    t = _norm_re_non.sub(" ", t)
    t = _norm_re_spc.sub(" ", t).strip()
    return t

# ---------- 健康检查 ----------
@app.get("/api/health")
def health():
    """健康检查端点 - 无数据库版本"""
    return {
        "ok": True,
        "status": "healthy",
        "database": "disabled",
        "message": "无数据库版本运行正常"
    }

# ---------- 搜索功能 - 返回模拟数据 ----------
@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    """搜索概念和字段 - 返回模拟数据"""
    if not q or not q.strip():
        return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}
    
    # 返回模拟数据
    mock_results = [
        {
            "hit_name": q,
            "canonical_name": f"{q.upper()}_CONCEPT",
            "field_name": f"{q}_FIELD",
            "j_series": j or "J3.2",
            "message_type": "MOCK"
        }
    ]
    
    return {
        "query": q.strip(),
        "j": j or "",
        "fuzzy": int(bool(fuzzy)),
        "results": mock_results,
        "note": "这是模拟数据 - 数据库已禁用"
    }

# ---------- 比较功能 - 返回模拟数据 ----------
@app.get("/api/compare")
def compare(q: str = Query(..., min_length=1)):
    """比较概念在不同规范中的定义 - 返回模拟数据"""
    return {
        "query": q,
        "detail": [
            {
                "canonical_name": q,
                "spec": "MIL-STD-6016",
                "definition": f"模拟定义: {q}",
                "note": "这是模拟数据 - 数据库已禁用"
            }
        ],
        "by_spec": [],
        "by_message": [],
    }

# ---------- 热门概念 - 返回模拟数据 ----------
@app.get("/api/review/top")
def review_top():
    """获取热门概念列表 - 返回模拟数据"""
    return [
        {"canonical_name": "Altitude", "fields": 15, "data_items": 8, "messages": 3, "specs": 2},
        {"canonical_name": "Heading", "fields": 12, "data_items": 6, "messages": 2, "specs": 2},
        {"canonical_name": "Speed", "fields": 10, "data_items": 5, "messages": 2, "specs": 1},
    ]

# ---------- 包含其他API模块 ----------
if PDF_API_AVAILABLE:
    try:
        include_pdf_routes(app)
        print("✓ PDF API模块已加载")
    except Exception as e:
        print(f"✗ PDF API模块加载失败: {e}")
        PDF_API_AVAILABLE = False

if MQTT_API_AVAILABLE:
    try:
        app.include_router(mqtt_router)
        print("✓ MQTT API模块已加载")
    except Exception as e:
        print(f"✗ MQTT API模块加载失败: {e}")
        MQTT_API_AVAILABLE = False

if UNIVERSAL_API_AVAILABLE:
    try:
        include_universal_routes(app)
        print("✓ Universal API模块已加载")
    except Exception as e:
        print(f"✗ Universal API模块加载失败: {e}")
        UNIVERSAL_API_AVAILABLE = False

if SEMANTIC_API_AVAILABLE:
    try:
        include_semantic_routes(app)
        print("✓ Semantic API模块已加载")
    except Exception as e:
        print(f"✗ Semantic API模块加载失败: {e}")
        SEMANTIC_API_AVAILABLE = False

if CDM_API_AVAILABLE:
    try:
        include_cdm_routes(app)
        print("✓ CDM API模块已加载")
    except Exception as e:
        print(f"✗ CDM API模块加载失败: {e}")
        CDM_API_AVAILABLE = False

if UNIFIED_API_AVAILABLE:
    try:
        include_unified_routes(app)
        print("✓ Unified API模块已加载")
    except Exception as e:
        print(f"✗ Unified API模块加载失败: {e}")
        UNIFIED_API_AVAILABLE = False

if MESSAGE_GENERATION_API_AVAILABLE:
    try:
        include_message_generation_routes(app)
        print("✓ 消息生成API模块已加载")
    except Exception as e:
        print(f"✗ 消息生成API模块加载失败: {e}")
        MESSAGE_GENERATION_API_AVAILABLE = False

# ---------- 启动信息 ----------
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动 MIL-STD-6016 API 服务器（无数据库版）")
    print("=" * 60)
    print("⚠️  数据库功能已禁用 - 用于诊断问题")
    print(f"📊 数据库状态: 已禁用")
    print(f"📄 PDF API: {'可用' if PDF_API_AVAILABLE else '不可用'}")
    print(f"📡 MQTT API: {'可用' if MQTT_API_AVAILABLE else '不可用'}")
    print(f"🌐 Universal API: {'可用' if UNIVERSAL_API_AVAILABLE else '不可用'}")
    print(f"🧠 Semantic API: {'可用' if SEMANTIC_API_AVAILABLE else '不可用'}")
    print(f"📋 CDM API: {'可用' if CDM_API_AVAILABLE else '不可用'}")
    print(f"🔗 Unified API: {'可用' if UNIFIED_API_AVAILABLE else '不可用'}")
    print(f"📦 消息生成API: {'可用' if MESSAGE_GENERATION_API_AVAILABLE else '不可用'}")
    print("=" * 60)
    print("🌐 服务地址: http://127.0.0.1:8000")
    print("📚 API文档: http://127.0.0.1:8000/docs")
    print("❤️  健康检查: http://127.0.0.1:8000/api/health")
    print("=" * 60)
    print()
    
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

