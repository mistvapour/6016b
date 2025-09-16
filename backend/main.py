from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os, io, csv, logging, re

from db import call_proc, query, exec_sql

app = FastAPI(title="MIL-STD-6016 Mini API", version="0.5.0")

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


# ---------- Models ----------
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


# ---------- utils ----------
_norm_re_non = re.compile(r"[^A-Z0-9]+")
_norm_re_spc = re.compile(r"\s+")


def normalize_canonical(s: str) -> str:
    """
    规范化名字：大写→去非字母数字→压空格。与批量 SQL 的规范化一致。
    """
    if s is None:
        return ""
    t = s.upper()
    t = _norm_re_non.sub(" ", t)
    t = _norm_re_spc.sub(" ", t).strip()
    return t


# ---------- Health ----------
@app.get("/api/health")
def health():
    try:
        row = query("SELECT DATABASE() AS db, VERSION() AS version")[0]
        return {"ok": True, **row}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


# ---------- 搜索（概念/字段，保留） ----------
@app.get("/api/search")
def search(
    q: Optional[str] = Query(None, description="关键词；可空"),
    j: Optional[str] = Query(None, description="J系列筛选，如 J3/J7；可空"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
):
    try:
        if not q or not q.strip():
            return {"query": "", "j": j or "", "fuzzy": int(bool(fuzzy)), "results": []}

        q = q.strip()
        sets = call_proc("sp_search_free", (q,))
        rows = sets[0] if sets else []

        if j:
            j_up = j.strip().upper()
            rows = [
                r
                for r in rows
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


# ---------- 新增：按 word_label 搜索（通过 概念↔字段 ↔数据项 拿 DFI/DUI） ----------
@app.get("/api/word/search")
def search_word_label(
    q: str = Query(..., min_length=1, description="word_label 关键词"),
    fuzzy: int = Query(1, ge=0, le=1, description="1=模糊(默认)，0=精确"),
    j: Optional[str] = Query(None, description="J 系列，如 J3/J7，可空"),
    limit: int = Query(200, ge=1, le=2000),
):
    """
    返回列：
      - word_label, dfi, dui
      - descriptor（= field_name）
      - position_bits（start_bit–end_bit）与 bit_range
      - resolution_coding（取自 field.notes）
      - j_series, code, edition, part_label
    关键点：通过 concept_binding 的两条 exact 绑定（field 与 data_item 在同一 concept_id）拼出 DFI/DUI。
    """
    try:
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
        JOIN field f
          ON f.word_id = w.word_id
        /* 概念↔字段（exact） */
        LEFT JOIN concept_binding cbf
          ON cbf.field_id = f.field_id AND cbf.eq_type = 'exact'
        /* 概念↔数据项（exact），与上面共享 concept_id */
        LEFT JOIN concept_binding cbd
          ON cbd.concept_id = cbf.concept_id AND cbd.eq_type = 'exact' AND cbd.data_item_id IS NOT NULL
        LEFT JOIN data_item di
          ON di.data_item_id = cbd.data_item_id
        LEFT JOIN message m
          ON m.message_id = w.message_id
        LEFT JOIN spec s
          ON s.spec_id = m.spec_id
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


# ---------- 新增：按字段名/word_label 搜索 data_item 候选 ----------
@app.get("/api/di/candidates")
def di_candidates(
    field_name: Optional[str] = Query(None, min_length=1, description="字段名关键词，如 'SECOND'"),
    word_label: Optional[str] = Query(None, min_length=1, description="word_label，如 'J10.2C2'"),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        if field_name:
            rows = query(
                "SELECT data_item_id, dfi, dui, di_name "
                "FROM data_item WHERE di_name LIKE %s "
                "ORDER BY dfi, dui LIMIT %s",
                (f"%{field_name}%", int(limit)),
            )
            return {"count": len(rows), "results": rows}

        if word_label:
            frows = query(
                "SELECT DISTINCT f.field_name "
                "FROM field f JOIN word w ON w.word_id = f.word_id "
                "WHERE w.word_label = %s",
                (word_label,),
            )
            if not frows:
                return {"count": 0, "results": []}
            likes = " OR ".join(["di_name LIKE %s" for _ in frows])
            like_args = tuple([f"%{r['field_name']}%" for r in frows])
            rows = query(
                f"SELECT data_item_id, dfi, dui, di_name FROM data_item WHERE {likes} "
                "ORDER BY dfi, dui LIMIT %s",
                like_args + (int(limit),),
            )
            return {"count": len(rows), "results": rows}

        return {"count": 0, "results": []}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


# ---------- 新增：将 field 绑定到 data_item（生成/复用 concept，并落两条 exact 绑定） ----------
@app.post("/api/bind/field-to-di")
def bind_field_to_di(body: BindFieldToDI):
    """
    语义：把某个 field 归入一个 concept，再让同一 concept 绑定到 data_item。
    实现：
      1) 先找 field 已有的概念绑定（eq_type='exact'）；
         若没有：为该字段名的“规范化名”创建/复用 concept，并创建 概念↔字段 的 exact 绑定；
      2) 再创建/更新 概念↔数据项 的 exact 绑定。
    注意：这符合你的库模型（eq_type 是匹配关系类型，不是对象类型）。
    """
    try:
        # 1) 取已有 concept_id（字段已绑定概念）
        rows = query(
            "SELECT concept_id FROM concept_binding WHERE field_id=%s AND eq_type='exact' LIMIT 1",
            (body.field_id,),
        )
        if rows:
            concept_id = rows[0]["concept_id"]
        else:
            # 没有的话：基于字段名规范化创建/复用 concept，并绑定 概念↔字段
            frow = query("SELECT field_name FROM field WHERE field_id=%s", (body.field_id,))
            if not frow:
                raise HTTPException(400, detail="field_id 不存在")
            canonical = normalize_canonical(frow[0]["field_name"])
            if not canonical:
                canonical = f"FIELD_{body.field_id}"

            # 插入或复用 concept
            exec_sql(
                "INSERT INTO concept (canonical_name) VALUES (%s) "
                "ON DUPLICATE KEY UPDATE canonical_name=VALUES(canonical_name)",
                (canonical,),
            )
            cid_row = query("SELECT concept_id FROM concept WHERE canonical_name=%s", (canonical,))
            if not cid_row:
                raise HTTPException(500, detail="创建/获取 concept 失败")
            concept_id = cid_row[0]["concept_id"]

            # 绑定 概念↔字段（exact）
            exec_sql(
                "INSERT INTO concept_binding (concept_id, eq_type, field_id, confidence, notes) "
                "VALUES (%s, 'exact', %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE confidence=VALUES(confidence), notes=VALUES(notes)",
                (concept_id, body.field_id, body.confidence or 0.95, body.notes),
            )

        # 2) 绑定 概念↔数据项（exact）
        exec_sql(
            "INSERT INTO concept_binding (concept_id, eq_type, data_item_id, confidence, notes) "
            "VALUES (%s, 'exact', %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE concept_id=VALUES(concept_id), "
            "  confidence=VALUES(confidence), notes=VALUES(notes)",
            (concept_id, body.data_item_id, body.confidence or 0.95, body.notes),
        )

        return {"ok": True, "concept_id": concept_id}
    except HTTPException:
        raise
    except Exception as e:
        # 更友好的错误提示（比如 concept 表不存在）
        msg = str(e)
        if "doesn't exist" in msg and ("concept" in msg or "concept_binding" in msg):
            raise HTTPException(
                500,
                detail="缺少 concept / concept_binding 表或结构，请先执行我给你的数据库合并脚本（建表与唯一键）。",
            )
        raise HTTPException(500, detail=msg)


# ---------- 其余接口：保持原状 ----------
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


# ---------- 导出 ----------
WHITELIST = {
    "export_concept_fields": [
        "canonical_name",
        "eq_type",
        "confidence",
        "dfi",
        "dui",
        "di_name",
        "field_id",
        "field_name",
        "start_bit",
        "end_bit",
        "bit_len",
        "word_label",
        "j_series",
        "code",
        "edition",
        "part_label",
    ],
    "export_concept_by_spec": ["name", "c", "e", "p", "field_bindings", "data_item_bindings"],
    "export_word_coverage": ["wl", "j", "c", "e", "p", "covered_bits", "total_bits", "coverage_pct"],
    "export_unbound_topN": ["data_item_id", "di_name", "refs"],
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
