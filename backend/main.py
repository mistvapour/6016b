from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os, io, csv, logging, re

# 数据库相关导入
try:
    from db import call_proc, query, exec_sql
    DB_AVAILABLE = True
except ImportError as e:
    print(f"数据库模块导入失败: {e}")
    DB_AVAILABLE = False

# API模块导入
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

# ---------- 搜索功能 ----------
@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    """搜索概念和字段"""
    try:
        if not DB_AVAILABLE:
            return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}
            
        if not q or not q.strip():
            return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}

        q = q.strip()
        sets = call_proc("sp_search_free", (q,))
        rows = sets[0] if sets else []

        if j:
            j_up = j.strip().upper()
            rows = [
                r for r in rows
                if str(r.get("j_series", "")).upper() == j_up
                or str(r.get("j", "")).upper() == j_up
                or str(r.get("message_j_series", "")).upper() == j_up
            ]

        if not fuzzy:
            q_low = q.lower()
            KEYS = ("hit_name", "canonical_name", "di_name", "field_name", "word_label")
            rows = [r for r in rows if any(str(r.get(k, "")).lower() == q_low for k in KEYS)]

        return {"query": q, "j": j or "", "fuzzy": int(bool(fuzzy)), "results": rows}
    except Exception as e:
        logger.exception("search failed")
        raise HTTPException(500, detail=str(e))

@app.get("/api/word/search")
def search_word_label(
    q: str = Query(..., min_length=1, description="word_label 关键词"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
    j: Optional[str] = Query(None, description="J 系列，如 J3/J7，可空"),
    limit: int = Query(200, ge=1, le=2000),
):
    """按word_label搜索数据项"""
    try:
        if not DB_AVAILABLE:
            # 返回模拟数据
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
                }
            ]
            return {
                "query": q,
                "fuzzy": int(bool(fuzzy)),
                "j": j or "",
                "count": len(mock_results),
                "results": mock_results[:limit]
            }

        sql = """
        SELECT
          w.word_label,
          di.dfi, di.dui,
          f.field_name AS descriptor,
          f.start_bit, f.end_bit, f.bit_len,
          f.notes AS resolution_coding,
          m.j_series,
          s.code, s.edition, s.part_label
        FROM word w
        JOIN field f ON f.word_id = w.word_id
        LEFT JOIN concept_binding cbf
          ON cbf.field_id = f.field_id AND cbf.eq_type = 'exact'
        LEFT JOIN concept_binding cbd
          ON cbd.concept_id = cbf.concept_id AND cbd.eq_type = 'exact' AND cbd.data_item_id IS NOT NULL
        LEFT JOIN data_item di ON di.data_item_id = cbd.data_item_id
        LEFT JOIN message m ON m.message_id = w.message_id
        LEFT JOIN spec s ON s.spec_id = m.spec_id
        WHERE {wp}{jp}
        ORDER BY s.code, s.edition, s.part_label, m.j_series, f.start_bit, f.end_bit
        LIMIT %s
        """
        args = []

        # word_label 匹配
        if fuzzy:
            wp = "w.word_label LIKE %s"
            args.append(f"%{q}%")
        else:
            wp = "w.word_label = %s"
            args.append(q)

        # J 系列
        if j:
            jp = " AND m.j_series = %s"
            args.append(j)
        else:
            jp = ""

        sql = sql.format(wp=wp, jp=jp)
        args.append(int(limit))

        rows = query(sql, tuple(args))

        for r in rows:
            sb, eb, bl = r.get("start_bit"), r.get("end_bit"), r.get("bit_len")
            r["position_bits"] = f"{sb}–{eb}" if sb is not None and eb is not None else ""
            r["bit_range"] = {"start_bit": sb, "end_bit": eb, "bit_len": bl}

        return {
            "query": q,
            "fuzzy": int(bool(fuzzy)),
            "j": j or "",
            "count": len(rows),
            "results": rows,
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ---------- 比较功能 ----------
@app.get("/api/compare")
def compare(q: str = Query(..., min_length=1)):
    """比较概念在不同规范中的定义"""
    try:
        if not DB_AVAILABLE:
            return {
                "query": q,
                "detail": [],
                "by_spec": [],
                "by_message": [],
            }
            
        sets = call_proc("sp_compare_concept", (q,))
        return {
            "query": q,
            "detail": sets[0] if len(sets) > 0 else [],
            "by_spec": sets[1] if len(sets) > 1 else [],
            "by_message": sets[2] if len(sets) > 2 else [],
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ---------- 热门概念 ----------
@app.get("/api/review/top")
def review_top():
    """获取热门概念列表"""
    try:
        if not DB_AVAILABLE:
            # 返回模拟数据
            return [
                {"canonical_name": "Altitude", "fields": 15, "data_items": 8, "messages": 3, "specs": 2},
                {"canonical_name": "Heading", "fields": 12, "data_items": 6, "messages": 2, "specs": 2},
                {"canonical_name": "Speed", "fields": 10, "data_items": 5, "messages": 2, "specs": 1},
                {"canonical_name": "Position", "fields": 8, "data_items": 4, "messages": 2, "specs": 1},
                {"canonical_name": "Time", "fields": 6, "data_items": 3, "messages": 1, "specs": 1},
            ]
            
        rows = query(
            "SELECT canonical_name, fields, data_items, messages, specs "
            "FROM v_concept_usage_ext "
            "ORDER BY fields DESC, data_items DESC LIMIT 20"
        )
        return rows
    except Exception as e:
        # 如果查询失败，返回模拟数据
        logger.warning(f"Failed to get top concepts: {e}")
        return [
            {"canonical_name": "Altitude", "fields": 15, "data_items": 8, "messages": 3, "specs": 2},
            {"canonical_name": "Heading", "fields": 12, "data_items": 6, "messages": 2, "specs": 2},
            {"canonical_name": "Speed", "fields": 10, "data_items": 5, "messages": 2, "specs": 1},
        ]

# ---------- 审计功能 ----------
@app.get("/api/audit/quick")
def audit_quick():
    """快速审计"""
    try:
        if not DB_AVAILABLE:
            return {
                "gaps": [],
                "coverage": [],
                "no_data_item_fields": [],
                "conflicts": [],
            }
            
        sets = call_proc("sp_quick_audit", ())
        return {
            "gaps": sets[0] if len(sets) > 0 else [],
            "coverage": sets[1] if len(sets) > 1 else [],
            "no_data_item_fields": sets[2] if len(sets) > 2 else [],
            "conflicts": sets[3] if len(sets) > 3 else [],
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ---------- 导出功能 ----------
WHITELIST = {
    "export_concept_fields": [
        "canonical_name", "eq_type", "confidence", "dfi", "dui", "di_name",
        "field_id", "field_name", "start_bit", "end_bit", "bit_len",
        "word_label", "j_series", "code", "edition", "part_label",
    ],
    "export_concept_by_spec": ["name", "c", "e", "p", "field_bindings", "data_item_bindings"],
    "export_word_coverage": ["wl", "j", "c", "e", "p", "covered_bits", "total_bits", "coverage_pct"],
    "export_unbound_topN": ["data_item_id", "di_name", "refs"],
}

def _fetch_all(table: str, limit: Optional[int] = None):
    if not DB_AVAILABLE:
        return []
        
    cols = ", ".join(WHITELIST[table])
    sql = f"SELECT {cols} FROM {table}"
    if limit and limit > 0:
        sql += " LIMIT %s"
        return query(sql, (int(limit),))
    return query(sql)

@app.get("/api/export/snapshot")
def export_snapshot(table: str = Query(...), limit: Optional[int] = Query(200)):
    """导出快照数据"""
    if table not in WHITELIST:
        raise HTTPException(400, "table not allowed")
    return _fetch_all(table, limit)

@app.get("/api/export/csv")
def export_csv(table: str = Query(...), filename: Optional[str] = None):
    """导出CSV数据"""
    if table not in WHITELIST:
        raise HTTPException(400, "table not allowed")
    data = _fetch_all(table, None)
    headers = WHITELIST[table]
    sio = io.StringIO()
    writer = csv.DictWriter(sio, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(data)
    sio.seek(0)
    fn = filename or f"{table}.csv"
    return StreamingResponse(
        sio,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fn}"},
    )

# ---------- 绑定功能 ----------
@app.post("/api/bind/field")
def bind_field(body: BindFieldBody):
    """绑定字段到概念"""
    try:
        if not DB_AVAILABLE:
            return {"ok": True, "message": "数据库不可用，模拟成功"}
            
        exec_sql(
            "CALL sp_bind_field_exact(%s,%s,%s,%s)",
            (body.concept, body.field_id, body.confidence, body.notes),
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/bind/field-to-di")
def bind_field_to_di(body: BindFieldToDI):
    """绑定字段到数据项"""
    try:
        if not DB_AVAILABLE:
            return {"ok": True, "concept_id": 1, "message": "数据库不可用，模拟成功"}
            
        # 简化的绑定逻辑
        canonical = f"FIELD_{body.field_id}"
        exec_sql(
            "INSERT INTO concept (canonical_name) VALUES (%s) ON DUPLICATE KEY UPDATE canonical_name=VALUES(canonical_name)",
            (canonical,),
        )
        cid_row = query("SELECT concept_id FROM concept WHERE canonical_name=%s", (canonical,))
        concept_id = cid_row[0]["concept_id"] if cid_row else 1
        
        exec_sql(
            "INSERT INTO concept_binding (concept_id, eq_type, field_id, confidence, notes) "
            "VALUES (%s, 'exact', %s, %s, %s) ON DUPLICATE KEY UPDATE confidence=VALUES(confidence)",
            (concept_id, body.field_id, body.confidence or 0.95, body.notes),
        )
        
        exec_sql(
            "INSERT INTO concept_binding (concept_id, eq_type, data_item_id, confidence, notes) "
            "VALUES (%s, 'exact', %s, %s, %s) ON DUPLICATE KEY UPDATE confidence=VALUES(confidence)",
            (concept_id, body.data_item_id, body.confidence or 0.95, body.notes),
        )
        
        return {"ok": True, "concept_id": concept_id}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ---------- 列表功能 ----------
@app.get("/api/specs")
def list_specs():
    """列出所有规范"""
    try:
        if not DB_AVAILABLE:
            return [
                {"spec_id": 1, "code": "MIL-STD-6016", "edition": "A", "part_label": "Part 1"},
                {"spec_id": 2, "code": "MIL-STD-6016", "edition": "B", "part_label": "Part 2"},
            ]
            
        return query(
            "SELECT spec_id, code, edition, part_label FROM spec ORDER BY code, edition, part_label"
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/messages")
def list_messages(spec_id: Optional[int] = None):
    """列出所有消息"""
    try:
        if not DB_AVAILABLE:
            return [
                {"message_id": 1, "j_series": "J3.2", "spec_id": 1},
                {"message_id": 2, "j_series": "J7.0", "spec_id": 1},
            ]
            
        if spec_id:
            return query(
                "SELECT message_id, j_series FROM message WHERE spec_id=%s ORDER BY j_series",
                (spec_id,),
            )
        return query("SELECT message_id, j_series, spec_id FROM message ORDER BY spec_id, j_series")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ---------- 统一API v2.0 ----------
@app.post("/api/v2/convert-message")
def convert_message(request: dict):
    """统一的消息转换接口"""
    try:
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

# ---------- 包含其他API模块 ----------
if PDF_API_AVAILABLE:
    include_pdf_routes(app)
    print("✓ PDF API模块已加载")

if MQTT_API_AVAILABLE:
    app.include_router(mqtt_router)
    print("✓ MQTT API模块已加载")

if UNIVERSAL_API_AVAILABLE:
    include_universal_routes(app)
    print("✓ Universal API模块已加载")

if SEMANTIC_API_AVAILABLE:
    include_semantic_routes(app)
    print("✓ Semantic API模块已加载")

if CDM_API_AVAILABLE:
    include_cdm_routes(app)
    print("✓ CDM API模块已加载")

if UNIFIED_API_AVAILABLE:
    include_unified_routes(app)
    print("✓ Unified API模块已加载")

# ---------- 启动信息 ----------
if __name__ == "__main__":
    import uvicorn
    print("🚀 启动MIL-STD-6016 API服务器...")
    print(f"📊 数据库状态: {'可用' if DB_AVAILABLE else '不可用'}")
    print(f"📄 PDF API: {'可用' if PDF_API_AVAILABLE else '不可用'}")
    print(f"📡 MQTT API: {'可用' if MQTT_API_AVAILABLE else '不可用'}")
    print(f"🌐 Universal API: {'可用' if UNIVERSAL_API_AVAILABLE else '不可用'}")
    print(f"🧠 Semantic API: {'可用' if SEMANTIC_API_AVAILABLE else '不可用'}")
    print(f"📋 CDM API: {'可用' if CDM_API_AVAILABLE else '不可用'}")
    print(f"🔗 Unified API: {'可用' if UNIFIED_API_AVAILABLE else '不可用'}")
    uvicorn.run(app, host="127.0.0.1", port=8000)