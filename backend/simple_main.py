#!/usr/bin/env python3
"""
简化版后端服务 - 用于测试API功能
暂时跳过PDF处理等复杂功能
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging

app = FastAPI(title="MIL-STD-6016 Mini API", version="0.5.0")

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

# 数据模型
class BindFieldBody(BaseModel):
    concept: str
    field_id: int
    confidence: Optional[float] = 0.95
    notes: Optional[str] = None

# 健康检查
@app.get("/api/health")
def health():
    try:
        return {
            "ok": True, 
            "database": "connected",
            "version": "0.5.0",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 统一API健康检查
@app.get("/api/v2/health")
def health_v2():
    try:
        module_status = {
            "pdf_processor": "healthy",
            "mqtt_processor": "healthy", 
            "semantic_interop": "healthy",
            "cdm_system": "healthy",
            "universal_import": "healthy"
        }
        
        return {
            "status": "ok",
            "version": "2.0.0",
            "modules": module_status,
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 搜索接口
@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    try:
        if not q or not q.strip():
            return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}

        # 模拟搜索结果
        mock_results = [
            {
                "hit_name": f"搜索结果: {q}",
                "canonical_name": q.upper(),
                "di_name": f"数据项_{q}",
                "field_name": f"字段_{q}",
                "word_label": f"WORD_{q}",
                "j_series": j or "J3",
                "confidence": 0.95
            }
        ]
        
        return {"query": q, "j": j or "", "fuzzy": int(bool(fuzzy)), "results": mock_results}
    except Exception as e:
        logger.exception("search failed")
        raise HTTPException(500, detail=str(e))

# 规范列表
@app.get("/api/specs")
def list_specs():
    try:
        # 模拟规范数据
        mock_specs = [
            {"spec_id": 1, "code": "MIL-STD-6016", "edition": "A", "part_label": "Part 1"},
            {"spec_id": 2, "code": "MIL-STD-6016", "edition": "B", "part_label": "Part 2"},
            {"spec_id": 3, "code": "MAVLink", "edition": "2.0", "part_label": "Protocol"},
        ]
        return mock_specs
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 消息列表
@app.get("/api/messages")
def list_messages(spec_id: Optional[int] = None):
    try:
        # 模拟消息数据
        mock_messages = [
            {"message_id": 1, "j_series": "J3.2", "spec_id": 1},
            {"message_id": 2, "j_series": "J3.3", "spec_id": 1},
            {"message_id": 3, "j_series": "J7.0", "spec_id": 2},
        ]
        
        if spec_id:
            return [msg for msg in mock_messages if msg["spec_id"] == spec_id]
        return mock_messages
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 统计信息
@app.get("/api/v2/statistics")
def get_statistics():
    try:
        stats = {
            "total_processed": 100,
            "success_rate": 0.95,
            "average_processing_time": 1.2,
            "supported_protocols": ["MIL-STD-6016", "MAVLink", "MQTT", "XML", "JSON", "CSV"],
            "supported_message_types": ["J_SERIES", "ATTITUDE", "CONNECT", "POSITION", "WEAPON_STATUS", "CUSTOM"],
            "active_mappings": 25,
            "system_uptime": "running",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": "2024-01-15T23:50:00Z"
        }
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 字段绑定
@app.post("/api/bind/field")
def bind_field(body: BindFieldBody):
    try:
        # 模拟绑定操作
        return {
            "ok": True,
            "concept": body.concept,
            "field_id": body.field_id,
            "confidence": body.confidence
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 热门概念（前端需要的端点）
@app.get("/api/review/top")
def review_top():
    try:
        # 模拟热门概念数据
        mock_top = [
            {
                "canonical_name": "ALTITUDE",
                "fields": 15,
                "data_items": 8,
                "messages": 12,
                "specs": 3
            },
            {
                "canonical_name": "POSITION",
                "fields": 22,
                "data_items": 14,
                "messages": 18,
                "specs": 4
            },
            {
                "canonical_name": "VELOCITY",
                "fields": 18,
                "data_items": 11,
                "messages": 15,
                "specs": 3
            },
            {
                "canonical_name": "ATTITUDE",
                "fields": 12,
                "data_items": 7,
                "messages": 9,
                "specs": 2
            },
            {
                "canonical_name": "TIME",
                "fields": 25,
                "data_items": 16,
                "messages": 20,
                "specs": 5
            }
        ]
        return mock_top
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 比较概念（前端需要的端点）
@app.get("/api/compare")
def compare(q: str = Query(..., min_length=1)):
    try:
        # 模拟比较结果
        mock_compare = {
            "query": q,
            "detail": [
                {
                    "canonical_name": q.upper(),
                    "fields": 5,
                    "data_items": 3,
                    "messages": 4,
                    "specs": 2
                }
            ],
            "by_spec": [
                {
                    "spec_code": "MIL-STD-6016",
                    "edition": "A",
                    "count": 3
                }
            ],
            "by_message": [
                {
                    "j_series": "J3.2",
                    "count": 2
                }
            ]
        }
        return mock_compare
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 审计快速检查（前端需要的端点）
@app.get("/api/audit/quick")
def audit_quick():
    try:
        # 模拟审计数据
        mock_audit = {
            "gaps": [
                {
                    "field_name": "示例字段1",
                    "missing_data_item": True
                }
            ],
            "coverage": [
                {
                    "concept": "ALTITUDE",
                    "coverage_percent": 85.5
                }
            ],
            "no_data_item_fields": [
                {
                    "field_id": 123,
                    "field_name": "示例字段2"
                }
            ],
            "conflicts": [
                {
                    "field_id": 456,
                    "conflict_type": "naming"
                }
            ]
        }
        return mock_audit
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 新增：按 word_label 搜索（前端需要的端点）
@app.get("/api/word/search")
def search_word_label(
    q: str = Query(..., min_length=1, description="word_label 关键词"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
    j: Optional[str] = Query(None, description="J 系列，如 J3/J7，可空"),
    limit: int = Query(200, ge=1, le=2000),
):
    """按word_label搜索数据项"""
    try:
        # 模拟搜索结果
        mock_results = [
            {
                "word_label": f"J3.2_{q.upper()}",
                "dfi": 1001,
                "dui": 2001,
                "descriptor": f"{q.upper()}_FIELD",
                "position_bits": "0-15",
                "bit_range": {"start_bit": 0, "end_bit": 15, "bit_len": 16},
                "resolution_coding": "16-bit integer",
                "j_series": j or "J3.2",
                "code": "MIL-STD-6016",
                "edition": "A",
                "part_label": "Part 1"
            },
            {
                "word_label": f"J7.0_{q.upper()}",
                "dfi": 1002,
                "dui": 2002,
                "descriptor": f"{q.upper()}_ALT",
                "position_bits": "16-31",
                "bit_range": {"start_bit": 16, "end_bit": 31, "bit_len": 16},
                "resolution_coding": "16-bit float",
                "j_series": j or "J7.0",
                "code": "MIL-STD-6016",
                "edition": "A",
                "part_label": "Part 1"
            }
        ]
        
        # 应用J系列过滤
        if j:
            mock_results = [r for r in mock_results if r["j_series"] == j]
        
        return {
            "query": q,
            "fuzzy": int(bool(fuzzy)),
            "j": j or "",
            "count": len(mock_results),
            "results": mock_results[:limit]
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# 统一API v2.0 端点
@app.post("/api/v2/convert-message")
def convert_message(request: dict):
    """统一的消息转换接口"""
    try:
        # 模拟消息转换结果
        mock_result = {
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
        
        return mock_result
        
    except Exception as e:
        logger.error(f"Message conversion failed: {e}")
        return {
            "success": False,
            "processing_time": 0.0,
            "errors": [str(e)]
        }

@app.get("/api/v2/concepts")
def get_concepts(
    category: Optional[str] = Query(None, description="概念类别"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """统一的概念管理接口"""
    try:
        # 模拟概念数据
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
            },
            {
                "path": "sem.time.timestamp",
                "data_type": "string",
                "unit": "ISO8601",
                "description": "时间戳",
                "source": "semantic"
            },
            {
                "path": "sem.weapon.status",
                "data_type": "enum",
                "unit": "status",
                "description": "武器状态",
                "source": "semantic"
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
        
    except Exception as e:
        logger.error(f"Concepts retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/mappings")
def get_mappings(
    source_protocol: Optional[str] = Query(None, description="源协议"),
    target_protocol: Optional[str] = Query(None, description="目标协议")
):
    """统一的映射管理接口"""
    try:
        # 模拟映射数据
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
            },
            {
                "mapping_key": "mqtt_to_semantic_position",
                "source_protocol": "MQTT",
                "target_protocol": "Semantic",
                "version": "1.0",
                "source": "semantic"
            },
            {
                "mapping_key": "xml_to_json_weapon_status",
                "source_protocol": "XML",
                "target_protocol": "JSON",
                "version": "1.0",
                "source": "semantic"
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
        
    except Exception as e:
        logger.error(f"Mappings retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 根路径
@app.get("/")
def root():
    return {
        "message": "MIL-STD-6016 API Server",
        "version": "0.5.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)