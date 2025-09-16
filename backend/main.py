from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os, io, csv, logging

from db import call_proc, query, exec_sql

app = FastAPI(title="MIL-STD-6016 Mini API", version="0.2.1")

# ---------- CORS ----------
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")


class BindFieldBody(BaseModel):
    concept: str
    field_id: int
    confidence: Optional[float] = 0.95
    notes: Optional[str] = None


@app.get("/api/health")
def health():
    try:
        row = query("SELECT DATABASE() AS db, VERSION() AS version")[0]
        return {"ok": True, **row}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    """
    - j:   J 系列筛选（可空）
    - fuzzy: 1=模糊(默认)，0=精确（后置等值过滤）
    - 继续复用存储过程 sp_search_free(q)
    """
    try:
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


@app.get("/api/compare")
def compare(q: str = Query(..., min_length=1)):
    try:
        sets = call_proc("sp_compare_concept", (q,))
        return {
            "query": q,
            "detail": sets[0] if len(sets) > 0 else [],
            "by_spec": sets[1] if len(sets) > 1 else [],
            "by_message": sets[2] if len(sets) > 2 else [],
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/api/review/top")
def review_top():
    try:
        rows = query(
            "SELECT canonical_name, fields, data_items, messages, specs "
            "FROM v_concept_usage_ext "
            "ORDER BY fields DESC, data_items DESC LIMIT 20"
        )
        return rows
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/api/audit/quick")
def audit_quick():
    try:
        sets = call_proc("sp_quick_audit", ())
        return {
            "gaps": sets[0] if len(sets) > 0 else [],
            "coverage": sets[1] if len(sets) > 1 else [],
            "no_data_item_fields": sets[2] if len(sets) > 2 else [],
            "conflicts": sets[3] if len(sets) > 3 else [],
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/api/exports/refresh")
def refresh_exports():
    try:
        call_proc("sp_refresh_exports", ())
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.post("/api/bind/field")
def bind_field(body: BindFieldBody):
    try:
        exec_sql(
            "CALL sp_bind_field_exact(%s,%s,%s,%s)",
            (body.concept, body.field_id, body.confidence, body.notes),
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/api/specs")
def list_specs():
    return query(
        "SELECT spec_id, code, edition, part_label FROM spec ORDER BY code, edition, part_label"
    )


@app.get("/api/messages")
def list_messages(spec_id: Optional[int] = None):
    if spec_id:
        return query(
            "SELECT message_id, j_series FROM message WHERE spec_id=%s ORDER BY j_series",
            (spec_id,),
        )
    return query("SELECT message_id, j_series, spec_id FROM message ORDER BY spec_id, j_series")


WHITELIST = {
    "export_concept_fields": [
        "canonical_name","eq_type","confidence","dfi","dui","di_name",
        "field_id","field_name","start_bit","end_bit","bit_len","word_label",
        "j_series","code","edition","part_label"
    ],
    "export_concept_by_spec": ["name","c","e","p","field_bindings","data_item_bindings"],
    "export_word_coverage": ["wl","j","c","e","p","covered_bits","total_bits","coverage_pct"],
    "export_unbound_topN": ["data_item_id","di_name","refs"],
}


def _fetch_all(table: str, limit: Optional[int] = None):
    cols = ", ".join(WHITELIST[table])
    sql = f"SELECT {cols} FROM {table}"
    if limit and limit > 0:
        sql += " LIMIT %s"
        return query(sql, (int(limit),))
    return query(sql)


@app.get("/api/export/snapshot")
def export_snapshot(table: str = Query(...), limit: Optional[int] = Query(200)):
    if table not in WHITELIST:
        raise HTTPException(400, "table not allowed")
    return _fetch_all(table, limit)


@app.get("/api/export/csv")
def export_csv(table: str = Query(...), filename: Optional[str] = None):
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
