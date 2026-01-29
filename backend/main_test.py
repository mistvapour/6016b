"""
测试版本的 main.py - 最小化配置，用于排查启动问题
只包含基本功能，不导入可能出错的模块
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

# 创建FastAPI应用
app = FastAPI(
    title="MIL-STD-6016 API (测试版)", 
    version="0.6.0-test",
    description="测试版本 - 军事标准6016数据分析和处理API"
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
        "name": "MIL-STD-6016 API (测试版)",
        "version": "0.6.0-test",
        "status": "running",
        "message": "这是一个测试版本，只包含基本功能",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
def health():
    """健康检查端点"""
    return {
        "ok": True,
        "status": "healthy",
        "message": "测试版本运行正常",
        "database": "not_checked"
    }

# ---------- 搜索功能（简化版） ----------
@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    """搜索概念和字段（测试版 - 返回模拟数据）"""
    if not q or not q.strip():
        return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}
    
    # 返回模拟数据
    mock_results = [
        {
            "hit_name": q,
            "canonical_name": f"{q.upper()}_CONCEPT",
            "field_name": f"{q}_FIELD",
            "j_series": j or "J3.2",
            "message_type": "TEST"
        }
    ]
    
    return {
        "query": q.strip(),
        "j": j or "",
        "fuzzy": int(bool(fuzzy)),
        "results": mock_results
    }

# ---------- 比较功能（简化版） ----------
@app.get("/api/compare")
def compare(q: str = Query(..., min_length=1)):
    """比较概念在不同规范中的定义（测试版）"""
    return {
        "query": q,
        "detail": [
            {
                "canonical_name": q,
                "spec": "MIL-STD-6016",
                "definition": f"测试定义: {q}"
            }
        ],
        "by_spec": [],
        "by_message": [],
    }

# ---------- 热门概念（简化版） ----------
@app.get("/api/review/top")
def review_top():
    """获取热门概念列表（测试版 - 返回模拟数据）"""
    return [
        {"canonical_name": "Altitude", "fields": 15, "data_items": 8, "messages": 3, "specs": 2},
        {"canonical_name": "Heading", "fields": 12, "data_items": 6, "messages": 2, "specs": 2},
        {"canonical_name": "Speed", "fields": 10, "data_items": 5, "messages": 2, "specs": 1},
    ]

# ---------- 测试端点 ----------
@app.get("/api/test")
def test():
    """测试端点"""
    return {
        "message": "测试成功！",
        "status": "ok",
        "endpoints": {
            "root": "/",
            "health": "/api/health",
            "search": "/api/search?q=test",
            "compare": "/api/compare?q=test",
            "top": "/api/review/top",
            "docs": "/docs"
        }
    }

# ---------- 启动信息 ----------
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动 MIL-STD-6016 API 服务器（测试版）")
    print("=" * 60)
    print("🌐 服务地址: http://127.0.0.1:8000")
    print("📚 API文档: http://127.0.0.1:8000/docs")
    print("❤️  健康检查: http://127.0.0.1:8000/api/health")
    print("🧪 测试端点: http://127.0.0.1:8000/api/test")
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

