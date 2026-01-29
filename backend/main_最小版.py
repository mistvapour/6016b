"""
main.py 最小版本 - 只保留基础功能，用于定位问题模块
所有自定义 API 模块已注释掉
"""
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os, io, csv, logging, re

print("=" * 60, file=sys.stderr)
print(">>> 开始加载 main.py（最小版本）", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# ---------- 数据库相关导入 ----------
print(">>> 正在加载数据库模块...", file=sys.stderr)
try:
    from db import call_proc, query, exec_sql
    DB_AVAILABLE = True
    print("✅ 数据库模块加载成功", file=sys.stderr)
except ImportError as e:
    print(f"❌ 数据库模块导入失败: {e}", file=sys.stderr)
    DB_AVAILABLE = False

# ==========================================
# 🛑 以下所有自定义 API 模块已注释掉
# ==========================================
# 用于定位哪个模块导致卡住
# ==========================================

# print(">>> 正在加载 PDF API 模块...", file=sys.stderr)
# try:
#     from pdf_api import include_pdf_routes
#     PDF_API_AVAILABLE = True
#     print("✅ PDF API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ PDF API模块导入失败: {e}", file=sys.stderr)
#     PDF_API_AVAILABLE = False
PDF_API_AVAILABLE = False

# print(">>> 正在加载 MQTT API 模块...", file=sys.stderr)
# try:
#     from mqtt_api import router as mqtt_router
#     MQTT_API_AVAILABLE = True
#     print("✅ MQTT API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ MQTT API模块导入失败: {e}", file=sys.stderr)
#     MQTT_API_AVAILABLE = False
MQTT_API_AVAILABLE = False

# print(">>> 正在加载 Universal API 模块...", file=sys.stderr)
# try:
#     from universal_import_api import include_universal_routes
#     UNIVERSAL_API_AVAILABLE = True
#     print("✅ Universal API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ Universal API模块导入失败: {e}", file=sys.stderr)
#     UNIVERSAL_API_AVAILABLE = False
UNIVERSAL_API_AVAILABLE = False

# print(">>> 正在加载 Semantic API 模块...", file=sys.stderr)
# try:
#     from semantic_interop_api import include_semantic_routes
#     SEMANTIC_API_AVAILABLE = True
#     print("✅ Semantic API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ Semantic API模块导入失败: {e}", file=sys.stderr)
#     SEMANTIC_API_AVAILABLE = False
SEMANTIC_API_AVAILABLE = False

# print(">>> 正在加载 CDM API 模块...", file=sys.stderr)
# try:
#     from cdm_api import include_cdm_routes
#     CDM_API_AVAILABLE = True
#     print("✅ CDM API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ CDM API模块导入失败: {e}", file=sys.stderr)
#     CDM_API_AVAILABLE = False
CDM_API_AVAILABLE = False

# print(">>> 正在加载 Unified API 模块...", file=sys.stderr)
# try:
#     from unified_api import include_unified_routes
#     UNIFIED_API_AVAILABLE = True
#     print("✅ Unified API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ Unified API模块导入失败: {e}", file=sys.stderr)
#     UNIFIED_API_AVAILABLE = False
UNIFIED_API_AVAILABLE = False

# print(">>> 正在加载消息生成API模块...", file=sys.stderr)
# try:
#     from message_generation_api import include_message_generation_routes
#     MESSAGE_GENERATION_API_AVAILABLE = True
#     print("✅ 消息生成API模块加载成功", file=sys.stderr)
# except ImportError as e:
#     print(f"❌ 消息生成API模块导入失败: {e}", file=sys.stderr)
#     MESSAGE_GENERATION_API_AVAILABLE = False
MESSAGE_GENERATION_API_AVAILABLE = False

print("=" * 60, file=sys.stderr)
print(">>> 模块导入完成，创建 FastAPI 应用", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# 创建FastAPI应用
app = FastAPI(
    title="MIL-STD-6016 Mini API (最小版)", 
    version="0.6.0-min",
    description="最小版本 - 用于定位问题模块"
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
        "name": "MIL-STD-6016 Mini API (最小版)",
        "version": "0.6.0-min",
        "status": "running",
        "message": "这是最小版本，所有自定义模块已注释",
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
    """健康检查端点"""
    try:
        if DB_AVAILABLE:
            row = query("SELECT DATABASE() AS db, VERSION() AS version")[0]
            return {"ok": True, "database": "connected", **row}
        else:
            return {"ok": True, "database": "not_available", "message": "数据库模块未加载"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ---------- 搜索功能（简化版，返回模拟数据） ----------
@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    """搜索概念和字段 - 返回模拟数据"""
    if not DB_AVAILABLE:
        return {"query": q or "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}
    
    if not q or not q.strip():
        return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}

    # 返回模拟数据
    return {
        "query": q.strip(),
        "j": j or "",
        "fuzzy": int(bool(fuzzy)),
        "results": [{"hit_name": q, "canonical_name": f"{q.upper()}_CONCEPT", "note": "模拟数据"}]
    }

# ==========================================
# 🛑 API 模块注册已注释掉
# ==========================================
# if PDF_API_AVAILABLE:
#     include_pdf_routes(app)
#     print("✓ PDF API模块已加载")
#
# if MQTT_API_AVAILABLE:
#     app.include_router(mqtt_router)
#     print("✓ MQTT API模块已加载")
# ... 其他模块也注释掉 ...

print("=" * 60, file=sys.stderr)
print(">>> FastAPI 应用创建完成", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# ---------- 启动信息 ----------
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动 MIL-STD-6016 API 服务器（最小版）")
    print("=" * 60)
    print(f"📊 数据库状态: {'可用' if DB_AVAILABLE else '不可用'}")
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

