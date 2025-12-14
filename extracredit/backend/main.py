"""Minimal FastAPI backend for the NL → SQL extra credit frontend demo.

It accepts a natural-language query and returns:
- the original query
- a generated SQL string (heuristic placeholder)
- tabular rows + column headers
- a placeholder LLM-style narrative

If a SQLite database exists at backend/sample.db, results are fetched from it.
Otherwise it falls back to in-memory mock data so the frontend still works.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sample.db"

MOCK_ROWS: List[Dict[str, Any]] = [
    {
        "order_id": 101,
        "customer": "Acme Co",
        "status": "delivered",
        "total": 1250.40,
        "city": "New York",
        "channel": "web",
        "created_at": "2024-10-02",
    },
    {
        "order_id": 102,
        "customer": "Bright Future",
        "status": "pending",
        "total": 980.00,
        "city": "Chicago",
        "channel": "mobile",
        "created_at": "2024-10-05",
    },
    {
        "order_id": 103,
        "customer": "Acme Co",
        "status": "processing",
        "total": 430.75,
        "city": "New York",
        "channel": "web",
        "created_at": "2024-10-09",
    },
    {
        "order_id": 104,
        "customer": "Helios Labs",
        "status": "delivered",
        "total": 2100.99,
        "city": "San Francisco",
        "channel": "sales",
        "created_at": "2024-09-15",
    },
    {
        "order_id": 105,
        "customer": "Bright Future",
        "status": "cancelled",
        "total": 150.00,
        "city": "Chicago",
        "channel": "web",
        "created_at": "2024-10-11",
    },
    {
        "order_id": 106,
        "customer": "Nexus Retail",
        "status": "delivered",
        "total": 780.50,
        "city": "Austin",
        "channel": "mobile",
        "created_at": "2024-10-03",
    },
    {
        "order_id": 107,
        "customer": "Summit Foods",
        "status": "pending",
        "total": 340.10,
        "city": "Denver",
        "channel": "web",
        "created_at": "2024-10-08",
    },
    {
        "order_id": 108,
        "customer": "Helios Labs",
        "status": "processing",
        "total": 665.45,
        "city": "San Francisco",
        "channel": "mobile",
        "created_at": "2024-10-10",
    },
]


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural-language question from the user.")
    limit: Optional[int] = Field(
        default=15, description="Optional row limit for the query results.", ge=1, le=500
    )
    use_mock: bool = Field(
        default=False, description="Force mock data even if a SQLite DB exists."
    )


class QueryResponse(BaseModel):
    original_query: str
    generated_sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    llm_output: str
    source: str


app = FastAPI(title="Extra Credit NL→SQL Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_sql(question: str, limit: Optional[int]) -> str:
    """Heuristic SQL generator to keep the demo self-contained."""
    safe_question = question.replace("'", "''").lower()
    conditions: List[str] = []

    if "pending" in safe_question:
        conditions.append("status = 'pending'")
    if "delivered" in safe_question:
        conditions.append("status = 'delivered'")
    if "processing" in safe_question:
        conditions.append("status = 'processing'")
    if "new york" in safe_question:
        conditions.append("city = 'New York'")
    if "san francisco" in safe_question:
        conditions.append("city = 'San Francisco'")
    if "chicago" in safe_question:
        conditions.append("city = 'Chicago'")
    if "mobile" in safe_question:
        conditions.append("channel = 'mobile'")
    if "web" in safe_question:
        conditions.append("channel = 'web'")

    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
    limit_clause = f" LIMIT {limit}" if limit else ""

    sql = (
        "SELECT order_id, customer, status, total, city, channel, created_at "
        f"FROM orders{where_clause} ORDER BY created_at DESC{limit_clause};"
    )
    return sql


def query_sqlite(sql: str) -> Optional[List[Dict[str, Any]]]:
    """Run SQL against sample.db if it exists."""
    if not DB_PATH.exists():
        return None

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute(sql).fetchall()
            return [dict(row) for row in results]
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail=f"SQLite error: {exc}") from exc


def filter_mock(question: str, limit: Optional[int]) -> List[Dict[str, Any]]:
    """Very light keyword filtering over the mock rows."""
    text = question.lower()
    rows = []
    for row in MOCK_ROWS:
        if "pending" in text and row["status"] != "pending":
            continue
        if "delivered" in text and row["status"] != "delivered":
            continue
        if "processing" in text and row["status"] != "processing":
            continue
        if "new york" in text and row["city"] != "New York":
            continue
        if "san francisco" in text and row["city"] != "San Francisco":
            continue
        if "chicago" in text and row["city"] != "Chicago":
            continue
        if "mobile" in text and row["channel"] != "mobile":
            continue
        if "web" in text and row["channel"] != "web":
            continue
        rows.append(row)

    if not rows:
        rows = MOCK_ROWS.copy()
    if limit:
        rows = rows[:limit]
    return rows


def llm_narrative(question: str, rows: List[Dict[str, Any]]) -> str:
    """Placeholder LLM output summarizing the rows."""
    total = sum(float(row["total"]) for row in rows)
    status_counts: Dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    status_text = ", ".join(f"{k}: {v}" for k, v in sorted(status_counts.items()))
    return (
        f"Your question: \"{question}\". Generated a filtered view over the orders table. "
        f"Returned {len(rows)} rows; total amount ${total:,.2f}. Status mix → {status_text or 'n/a'}. "
        "Swap in your real LLM call here."
    )


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/query", response_model=QueryResponse)
def handle_query(payload: QueryRequest) -> QueryResponse:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query text is required.")

    sql = build_sql(payload.query, payload.limit)

    rows: Optional[List[Dict[str, Any]]] = None
    source = "mock"

    if not payload.use_mock:
        rows = query_sqlite(sql)
        source = "sqlite" if rows is not None else "mock"

    if rows is None:
        rows = filter_mock(payload.query, payload.limit)

    columns = list(rows[0].keys()) if rows else []

    response = QueryResponse(
        original_query=payload.query,
        generated_sql=sql,
        columns=columns,
        rows=rows,
        llm_output=llm_narrative(payload.query, rows),
        source=source,
    )
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
