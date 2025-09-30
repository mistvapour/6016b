from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os, io, csv

app = FastAPI(title="MIL-STD-6016 Mini API", version="0.2.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BindFieldBody(BaseModel):
    concept: str
    field_id: int
    confidence: Optional[float] = 0.95
    notes: Optional[str] = None

@app.get("/api/health")
def health():
    return {"ok": True, "db": "mock", "version": "0.2.0"}

@app.get("/api/search")
def search(q: str = Query(..., min_length=1)):
    # Mock data for testing
    return {
        "query": q,
        "results": [
            {
                "source": "mock",
                "hit_name": f"Mock result for {q}",
                "canonical_name": f"Canonical {q}",
                "code": "MIL-STD-6016",
                "edition": "A",
                "part_label": "Part 1",
                "j_series": "J1.0",
                "word_label": "Word1",
                "field_name": "Field1",
                "start_bit": 0,
                "end_bit": 15,
                "field_id": 1
            }
        ]
    }

@app.get("/api/compare")
def compare(q: str = Query(..., min_length=1)):
    return {
        "query": q,
        "detail": [],
        "by_spec": [
            {
                "code": "MIL-STD-6016",
                "edition": "A",
                "part_label": "Part 1",
                "field_bindings": 5
            }
        ],
        "by_message": []
    }

@app.get("/api/review/top")
def review_top():
    return [
        {
            "canonical_name": "Mock Concept",
            "fields": 10,
            "data_items": 5,
            "messages": 3,
            "specs": 1
        }
    ]

@app.get("/api/audit/quick")
def audit_quick():
    return {
        "gaps": [],
        "coverage": [],
        "no_data_item_fields": [],
        "conflicts": []
    }

@app.post("/api/exports/refresh")
def refresh_exports():
    return {"ok": True}

@app.post("/api/bind/field")
def bind_field(body: BindFieldBody):
    return {"ok": True}

@app.get("/api/specs")
def list_specs():
    return [
        {"spec_id": 1, "code": "MIL-STD-6016", "edition": "A", "part_label": "Part 1"}
    ]

@app.get("/api/messages")
def list_messages(spec_id: Optional[int] = None):
    return [
        {"message_id": 1, "j_series": "J1.0", "spec_id": 1}
    ]

@app.get("/api/export/snapshot")
def export_snapshot(table: str = Query(...), limit: Optional[int] = Query(200)):
    return [{"mock": "data"}]

@app.get("/api/export/csv")
def export_csv(table: str = Query(...), filename: Optional[str] = None):
    data = [{"mock": "data"}]
    headers = ["mock"]
    sio = io.StringIO()
    writer = csv.DictWriter(sio, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(data)
    sio.seek(0)
    fn = filename or f"{table}.csv"
    return StreamingResponse(sio, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={fn}"})

