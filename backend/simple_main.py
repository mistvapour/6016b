#!/usr/bin/env python3
"""
简化版后端服务 - 用于测试API功能
暂时跳过PDF处理等复杂功能
"""
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import tempfile
import json
from pathlib import Path

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

class PDFProcessRequest(BaseModel):
    standard: str = "MIL-STD-6016"
    edition: str = "B"
    output_dir: Optional[str] = None

class ProcessingResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CustomStandardRequest(BaseModel):
    name: str
    description: str
    edition: str
    message_types: List[str]
    fields: List[Dict[str, Any]]

class StandardDefinition(BaseModel):
    name: str
    description: str
    edition: str
    message_types: List[str]
    fields: List[Dict[str, Any]]

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

# ---------- PDF处理API ----------
# 支持的标准定义
SUPPORTED_STANDARDS = {
    "MIL-STD-6016": {
        "name": "MIL-STD-6016",
        "description": "美军标准6016 - 战术数据链消息标准",
        "editions": ["A", "B", "C"],
        "message_types": ["J3.2", "J7.0", "J10.2", "J12.0", "J13.0"]
    },
    "MIL-STD-3011": {
        "name": "MIL-STD-3011", 
        "description": "美军标准3011 - 联合战术信息分发系统",
        "editions": ["A", "B"],
        "message_types": ["J2.0", "J2.2", "J3.0", "J3.1", "J3.3"]
    },
    "STANAG-5516": {
        "name": "STANAG-5516",
        "description": "北约标准5516 - 战术数据交换",
        "editions": ["1", "2", "3"],
        "message_types": ["J2.0", "J3.0", "J7.0", "J12.0"]
    },
    "MAVLink": {
        "name": "MAVLink",
        "description": "微型飞行器通信协议",
        "editions": ["1.0", "2.0"],
        "message_types": ["HEARTBEAT", "ATTITUDE", "POSITION", "GPS_RAW_INT"]
    },
    "NMEA-0183": {
        "name": "NMEA-0183",
        "description": "海洋电子设备数据格式",
        "editions": ["2.0", "2.1", "2.2", "2.3"],
        "message_types": ["GGA", "RMC", "VTG", "GLL", "GSA"]
    },
    "ARINC-429": {
        "name": "ARINC-429",
        "description": "航空电子设备数字信息传输",
        "editions": ["15", "16", "17"],
        "message_types": ["A429", "A629"]
    }
}

def get_standard_info(standard: str, edition: str = None):
    """获取标准信息"""
    if standard not in SUPPORTED_STANDARDS:
        return None
    info = SUPPORTED_STANDARDS[standard].copy()
    if edition and edition in info["editions"]:
        info["selected_edition"] = edition
    return info

def generate_custom_result(custom_standard: Dict[str, Any], filename: str):
    """根据自定义标准生成处理结果"""
    fields = custom_standard.get("fields", [])
    
    # 计算消息总长度
    max_end_bit = 0
    for field in fields:
        bit_range = field.get("bit_range", {})
        if bit_range.get("end", 0) > max_end_bit:
            max_end_bit = bit_range.get("end", 0)
    
    message_length = max_end_bit + 1
    
    return {
        "sim": {
            "message_type": custom_standard.get("message_types", ["CUSTOM"])[0],
            "fields": fields,
            "total_fields": len(fields),
            "message_length": message_length,
            "standard": custom_standard.get("name", "Custom"),
            "edition": custom_standard.get("edition", "1.0")
        },
        "validation_result": {
            "valid": True,
            "errors": [],
            "warnings": ["部分字段缺少单位信息"] if any(not field.get("units") for field in fields) else [],
            "coverage": 0.85 + (len(fields) * 0.05),
            "confidence": sum(field.get("confidence", 0.8) for field in fields) / len(fields) if fields else 0.8
        },
        "yaml_files": [f"{filename}_processed_custom_{custom_standard.get('name', 'standard')}.yaml"],
        "report": {
            "processing_time": 2.5 + (len(fields) * 0.5),
            "pages_processed": 1,
            "tables_extracted": 1,
            "fields_identified": len(fields),
            "standard_detected": custom_standard.get("name", "Custom"),
            "edition_detected": custom_standard.get("edition", "1.0"),
            "is_custom": True
        }
    }

def generate_mock_result(standard: str, edition: str, filename: str):
    """根据标准生成模拟处理结果"""
    standard_info = get_standard_info(standard, edition)
    if not standard_info:
        standard_info = SUPPORTED_STANDARDS["MIL-STD-6016"]
    
    # 根据标准类型生成不同的字段
    if standard == "MIL-STD-6016":
        fields = [
            {
                "field_name": "ALTITUDE",
                "bit_range": {"start": 0, "end": 15, "length": 16},
                "description": "飞行器高度信息",
                "units": ["meters", "feet"],
                "confidence": 0.95,
                "data_type": "uint16"
            },
            {
                "field_name": "HEADING", 
                "bit_range": {"start": 16, "end": 31, "length": 16},
                "description": "航向角",
                "units": ["degrees"],
                "confidence": 0.92,
                "data_type": "uint16"
            },
            {
                "field_name": "SPEED",
                "bit_range": {"start": 32, "end": 47, "length": 16},
                "description": "飞行速度",
                "units": ["knots", "m/s"],
                "confidence": 0.88,
                "data_type": "uint16"
            }
        ]
        message_type = "J3.2"
        message_length = 48
        
    elif standard == "MIL-STD-3011":
        fields = [
            {
                "field_name": "LATITUDE",
                "bit_range": {"start": 0, "end": 31, "length": 32},
                "description": "纬度坐标",
                "units": ["degrees"],
                "confidence": 0.98,
                "data_type": "int32"
            },
            {
                "field_name": "LONGITUDE",
                "bit_range": {"start": 32, "end": 63, "length": 32},
                "description": "经度坐标", 
                "units": ["degrees"],
                "confidence": 0.98,
                "data_type": "int32"
            }
        ]
        message_type = "J2.0"
        message_length = 64
        
    elif standard == "STANAG-5516":
        fields = [
            {
                "field_name": "TRACK_NUMBER",
                "bit_range": {"start": 0, "end": 15, "length": 16},
                "description": "航迹编号",
                "units": [],
                "confidence": 0.99,
                "data_type": "uint16"
            },
            {
                "field_name": "POSITION_QUALITY",
                "bit_range": {"start": 16, "end": 23, "length": 8},
                "description": "位置质量",
                "units": [],
                "confidence": 0.85,
                "data_type": "uint8"
            }
        ]
        message_type = "J2.0"
        message_length = 24
        
    elif standard == "MAVLink":
        fields = [
            {
                "field_name": "ROLL",
                "bit_range": {"start": 0, "end": 31, "length": 32},
                "description": "横滚角",
                "units": ["radians"],
                "confidence": 0.95,
                "data_type": "float32"
            },
            {
                "field_name": "PITCH",
                "bit_range": {"start": 32, "end": 63, "length": 32},
                "description": "俯仰角",
                "units": ["radians"],
                "confidence": 0.95,
                "data_type": "float32"
            },
            {
                "field_name": "YAW",
                "bit_range": {"start": 64, "end": 95, "length": 32},
                "description": "偏航角",
                "units": ["radians"],
                "confidence": 0.95,
                "data_type": "float32"
            }
        ]
        message_type = "ATTITUDE"
        message_length = 96
        
    elif standard == "NMEA-0183":
        fields = [
            {
                "field_name": "LATITUDE",
                "bit_range": {"start": 0, "end": 31, "length": 32},
                "description": "纬度",
                "units": ["degrees"],
                "confidence": 0.99,
                "data_type": "float32"
            },
            {
                "field_name": "LONGITUDE",
                "bit_range": {"start": 32, "end": 63, "length": 32},
                "description": "经度",
                "units": ["degrees"],
                "confidence": 0.99,
                "data_type": "float32"
            },
            {
                "field_name": "ALTITUDE",
                "bit_range": {"start": 64, "end": 95, "length": 32},
                "description": "海拔高度",
                "units": ["meters"],
                "confidence": 0.97,
                "data_type": "float32"
            }
        ]
        message_type = "GGA"
        message_length = 128
        
    elif standard == "ARINC-429":
        fields = [
            {
                "field_name": "DATA_WORD",
                "bit_range": {"start": 0, "end": 31, "length": 32},
                "description": "数据字",
                "units": [],
                "confidence": 0.99,
                "data_type": "uint32"
            },
            {
                "field_name": "LABEL",
                "bit_range": {"start": 0, "end": 7, "length": 8},
                "description": "标签",
                "units": [],
                "confidence": 0.99,
                "data_type": "uint8"
            }
        ]
        message_type = "A429"
        message_length = 32
        
    else:
        # 默认MIL-STD-6016格式
        fields = [
            {
                "field_name": "DEFAULT_FIELD",
                "bit_range": {"start": 0, "end": 15, "length": 16},
                "description": "默认字段",
                "units": [],
                "confidence": 0.8,
                "data_type": "uint16"
            }
        ]
        message_type = "UNKNOWN"
        message_length = 16
    
    return {
        "sim": {
            "message_type": message_type,
            "fields": fields,
            "total_fields": len(fields),
            "message_length": message_length,
            "standard": standard,
            "edition": edition
        },
        "validation_result": {
            "valid": True,
            "errors": [],
            "warnings": ["部分字段缺少单位信息"] if any(not field.get("units") for field in fields) else [],
            "coverage": 0.85 + (len(fields) * 0.05),
            "confidence": sum(field.get("confidence", 0.8) for field in fields) / len(fields)
        },
        "yaml_files": [f"{filename}_processed_{standard}_{edition}.yaml"],
        "report": {
            "processing_time": 2.5 + (len(fields) * 0.5),
            "pages_processed": 1,
            "tables_extracted": 1,
            "fields_identified": len(fields),
            "standard_detected": standard,
            "edition_detected": edition
        }
    }

@app.get("/api/pdf/standards")
def get_supported_standards():
    """获取支持的标准列表"""
    return {
        "success": True,
        "standards": SUPPORTED_STANDARDS,
        "total": len(SUPPORTED_STANDARDS)
    }

@app.get("/api/pdf/standards/{standard}")
def get_standard_details(standard: str):
    """获取特定标准的详细信息"""
    info = get_standard_info(standard)
    if not info:
        raise HTTPException(status_code=404, detail=f"不支持的标准: {standard}")
    return {
        "success": True,
        "standard": info
    }

@app.post("/api/pdf/standards/custom", response_model=ProcessingResult)
def create_custom_standard(standard_def: CustomStandardRequest):
    """创建自定义标准"""
    try:
        # 验证标准定义
        if not standard_def.name or not standard_def.name.strip():
            raise HTTPException(status_code=400, detail="标准名称不能为空")
        
        if not standard_def.fields or len(standard_def.fields) == 0:
            raise HTTPException(status_code=400, detail="至少需要定义一个字段")
        
        # 验证字段定义
        for i, field in enumerate(standard_def.fields):
            if not field.get("field_name"):
                raise HTTPException(status_code=400, detail=f"字段 {i+1} 缺少名称")
            
            if not field.get("bit_range"):
                raise HTTPException(status_code=400, detail=f"字段 {field['field_name']} 缺少位范围定义")
            
            bit_range = field["bit_range"]
            if not isinstance(bit_range, dict) or "start" not in bit_range or "end" not in bit_range:
                raise HTTPException(status_code=400, detail=f"字段 {field['field_name']} 的位范围格式不正确")
            
            if bit_range["start"] < 0 or bit_range["end"] < bit_range["start"]:
                raise HTTPException(status_code=400, detail=f"字段 {field['field_name']} 的位范围值无效")
        
        # 生成标准ID
        standard_id = f"CUSTOM_{standard_def.name.upper().replace(' ', '_')}_{standard_def.edition}"
        
        # 将自定义标准添加到支持的标准中
        SUPPORTED_STANDARDS[standard_id] = {
            "name": standard_def.name,
            "description": standard_def.description,
            "editions": [standard_def.edition],
            "message_types": standard_def.message_types,
            "fields": standard_def.fields,
            "is_custom": True
        }
        
        return ProcessingResult(
            success=True,
            message=f"自定义标准 '{standard_def.name}' 创建成功",
            data={
                "standard_id": standard_id,
                "standard": SUPPORTED_STANDARDS[standard_id]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create custom standard: {e}")
        return ProcessingResult(
            success=False,
            message="创建自定义标准失败",
            error=str(e)
        )

@app.post("/api/pdf/upload/custom", response_model=ProcessingResult)
async def upload_pdf_with_custom_standard(
    file: UploadFile = File(...),
    standard_definition: str = Form(...),  # JSON字符串
    output_dir: Optional[str] = Form(None)
):
    """使用自定义标准上传并处理PDF文件"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 解析自定义标准定义
        try:
            custom_standard = json.loads(standard_definition)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="标准定义格式不正确")
        
        # 验证标准定义
        required_fields = ["name", "edition", "fields"]
        for field in required_fields:
            if field not in custom_standard:
                raise HTTPException(status_code=400, detail=f"标准定义缺少必需字段: {field}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 使用自定义标准生成处理结果
            mock_result = generate_custom_result(custom_standard, file.filename)
            
            return ProcessingResult(
                success=True,
                message=f"PDF文件 {file.filename} 处理成功 (自定义标准: {custom_standard['name']} {custom_standard['edition']})",
                data=mock_result
            )
            
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom PDF processing failed: {e}")
        return ProcessingResult(
            success=False,
            message="PDF处理失败",
            error=str(e)
        )

@app.post("/api/pdf/upload", response_model=ProcessingResult)
async def upload_pdf(
    file: UploadFile = File(...),
    standard: str = Form("MIL-STD-6016"),
    edition: str = Form("B"),
    output_dir: Optional[str] = Form(None)
):
    """上传并处理PDF文件"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 验证标准是否支持
        if standard not in SUPPORTED_STANDARDS:
            raise HTTPException(status_code=400, detail=f"不支持的标准: {standard}")
        
        # 验证版本是否支持
        standard_info = SUPPORTED_STANDARDS[standard]
        if edition not in standard_info["editions"]:
            raise HTTPException(status_code=400, detail=f"标准 {standard} 不支持版本 {edition}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 根据标准生成处理结果
            mock_result = generate_mock_result(standard, edition, file.filename)
            
            return ProcessingResult(
                success=True,
                message=f"PDF文件 {file.filename} 处理成功 (标准: {standard} {edition})",
                data=mock_result
            )
            
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return ProcessingResult(
            success=False,
            message="PDF处理失败",
            error=str(e)
        )

@app.post("/api/pdf/process", response_model=ProcessingResult)
async def process_pdf_file_endpoint(
    file_path: str = Query(..., description="PDF文件路径"),
    standard: str = Query("MIL-STD-6016", description="标准类型"),
    edition: str = Query("B", description="版本"),
    output_dir: Optional[str] = Query(None, description="输出目录")
):
    """处理指定路径的PDF文件"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF文件不存在")
        
        if not file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 模拟处理结果
        mock_result = {
            "sim": {
                "message_type": "J7.0",
                "fields": [
                    {
                        "field_name": "POSITION_LAT",
                        "bit_range": {"start": 0, "end": 31, "length": 32},
                        "description": "纬度位置",
                        "units": ["degrees"],
                        "confidence": 0.98
                    },
                    {
                        "field_name": "POSITION_LON",
                        "bit_range": {"start": 32, "end": 63, "length": 32},
                        "description": "经度位置",
                        "units": ["degrees"],
                        "confidence": 0.98
                    }
                ],
                "total_fields": 2,
                "message_length": 64
            },
            "validation_result": {
                "valid": True,
                "errors": [],
                "warnings": [],
                "coverage": 0.95,
                "confidence": 0.98
            },
            "yaml_files": [f"{os.path.basename(file_path)}_processed.yaml"],
            "report": {
                "processing_time": 1.8,
                "pages_processed": 2,
                "tables_extracted": 2,
                "fields_identified": 2
            }
        }
        
        return ProcessingResult(
            success=True,
            message=f"PDF文件 {os.path.basename(file_path)} 处理成功",
            data=mock_result
        )
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return ProcessingResult(
            success=False,
            message="PDF处理失败",
            error=str(e)
        )

@app.get("/api/pdf/status/{task_id}")
def get_processing_status(task_id: str):
    """获取PDF处理状态"""
    # 模拟处理状态
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "message": "处理完成"
    }

@app.get("/api/pdf/download/{filename}")
def download_processed_file(filename: str):
    """下载处理后的文件"""
    # 模拟文件下载
    mock_content = f"# 处理结果文件: {filename}\n# 这是模拟的YAML文件内容\nfields:\n  - name: FIELD1\n    bits: 0-15\n  - name: FIELD2\n    bits: 16-31"
    
    return JSONResponse(
        content={"content": mock_content, "filename": filename},
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

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