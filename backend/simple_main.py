#!/usr/bin/env python3
"""
简化的后端启动脚本
避免复杂的依赖问题
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging

# 创建FastAPI应用
app = FastAPI(
    title="MIL-STD-6016 Mini API", 
    version="0.6.0",
    description="军事标准6016数据分析和处理API"
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

# ---------- 健康检查 ----------
@app.get("/api/health")
def health():
    """健康检查端点"""
    return {
        "ok": True, 
        "database": "not_available", 
        "message": "简化模式运行",
        "version": "0.6.0"
    }

# ---------- 搜索功能 ----------
@app.get("/api/search")
def search(
    q: Optional[str] = None,
    j: Optional[str] = None,
    fuzzy: int = 1,
):
    """搜索概念和字段"""
    return {
        "query": q or "",
        "j": j or "",
        "fuzzy": int(bool(fuzzy)),
        "results": [
            {
                "canonical_name": "Altitude",
                "field_name": "altitude_field",
                "j_series": "J3.2",
                "confidence": 0.95
            },
            {
                "canonical_name": "Heading", 
                "field_name": "heading_field",
                "j_series": "J3.2",
                "confidence": 0.90
            }
        ]
    }

# ---------- 热门概念 ----------
@app.get("/api/review/top")
def review_top():
    """获取热门概念列表"""
    return [
        {"canonical_name": "Altitude", "fields": 15, "data_items": 8, "messages": 3, "specs": 2},
        {"canonical_name": "Heading", "fields": 12, "data_items": 6, "messages": 2, "specs": 2},
        {"canonical_name": "Speed", "fields": 10, "data_items": 5, "messages": 2, "specs": 1},
        {"canonical_name": "Position", "fields": 8, "data_items": 4, "messages": 2, "specs": 1},
        {"canonical_name": "Time", "fields": 6, "data_items": 3, "messages": 1, "specs": 1},
    ]

# ---------- 统一API v2.0 ----------
@app.post("/api/v2/convert-message")
def convert_message(request: dict):
    """统一的消息转换接口"""
    return {
        "success": True,
        "target_message": {
            "message_type": request.get("target_message_type", "POSITION"),
            "protocol": request.get("target_protocol", "MQTT"),
            "data": {
                "converted_field": "converted_value",
                "timestamp": "2024-01-15T23:58:00Z",
                "source": request.get("source_message", {}).get("protocol", "MIL-STD-6016")
            },
            "metadata": {
                "conversion_method": "cdm",
                "confidence": 0.95
            }
        },
        "processing_time": 0.123,
        "confidence": 0.95,
        "errors": [],
        "warnings": [],
        "metadata": {
            "source_protocol": request.get("source_message", {}).get("protocol", "MIL-STD-6016"),
            "target_protocol": request.get("target_protocol", "MQTT"),
            "conversion_method": "cdm"
        }
    }

@app.get("/api/v2/concepts")
def get_concepts(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """统一的概念管理接口"""
    mock_concepts = [
        {
            "path": "position.altitude",
            "data_type": "float",
            "unit": "meters",
            "description": "飞行器高度信息",
            "source": "cdm"
        },
        {
            "path": "position.latitude",
            "data_type": "float", 
            "unit": "degrees",
            "description": "纬度坐标",
            "source": "cdm"
        },
        {
            "path": "position.longitude",
            "data_type": "float",
            "unit": "degrees", 
            "description": "经度坐标",
            "source": "cdm"
        },
        {
            "path": "velocity.speed",
            "data_type": "float",
            "unit": "m/s",
            "description": "飞行速度",
            "source": "cdm"
        },
        {
            "path": "attitude.roll",
            "data_type": "float",
            "unit": "degrees",
            "description": "横滚角",
            "source": "cdm"
        },
        {
            "path": "attitude.pitch",
            "data_type": "float",
            "unit": "degrees",
            "description": "俯仰角",
            "source": "cdm"
        },
        {
            "path": "attitude.yaw",
            "data_type": "float",
            "unit": "degrees",
            "description": "偏航角",
            "source": "cdm"
        }
    ]
    
    # 应用过滤
    filtered_concepts = mock_concepts
    if category:
        filtered_concepts = [c for c in filtered_concepts if category.lower() in c.get("path", "").lower()]
    
    if search:
        filtered_concepts = [c for c in filtered_concepts if search.lower() in c.get("description", "").lower()]
    
    return {
        "success": True,
        "concepts": filtered_concepts,
        "total": len(filtered_concepts),
        "sources": {
            "cdm": len([c for c in filtered_concepts if c["source"] == "cdm"]),
            "semantic": len([c for c in filtered_concepts if c["source"] == "semantic"])
        }
    }

@app.get("/api/v2/mappings")
def get_mappings(
    source_protocol: Optional[str] = None,
    target_protocol: Optional[str] = None
):
    """统一的映射管理接口"""
    mock_mappings = [
        {
            "mapping_key": "milstd6016_to_mqtt_position",
            "source_protocol": "MIL-STD-6016",
            "target_protocol": "MQTT",
            "version": "1.0",
            "source": "cdm"
        },
        {
            "mapping_key": "milstd6016_to_mavlink_attitude",
            "source_protocol": "MIL-STD-6016", 
            "target_protocol": "MAVLink",
            "version": "1.0",
            "source": "cdm"
        },
        {
            "mapping_key": "mavlink_to_mqtt_position",
            "source_protocol": "MAVLink",
            "target_protocol": "MQTT", 
            "version": "1.0",
            "source": "cdm"
        }
    ]
    
    # 应用过滤
    filtered_mappings = mock_mappings
    if source_protocol:
        filtered_mappings = [m for m in filtered_mappings if m["source_protocol"] == source_protocol]
    
    if target_protocol:
        filtered_mappings = [m for m in filtered_mappings if m["target_protocol"] == target_protocol]
    
    return {
        "success": True,
        "mappings": filtered_mappings,
        "total": len(filtered_mappings),
        "sources": {
            "cdm": len([m for m in filtered_mappings if m["source"] == "cdm"]),
            "semantic": len([m for m in filtered_mappings if m["source"] == "semantic"])
        }
    }

# ---------- 启动信息 ----------
if __name__ == "__main__":
    import uvicorn
    print("🚀 启动MIL-STD-6016 API服务器 (简化模式)...")
    print("📊 数据库状态: 不可用 (简化模式)")
    print("🌐 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)