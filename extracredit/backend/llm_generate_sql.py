from __future__ import annotations

import argparse
import re
from typing import Optional

from gemini_client import build_gemini_model, is_gemini_configured


SCHEMA_HINT = """SQLite schema:
Table: orders
Columns:
- order_id INTEGER
- customer TEXT
- status TEXT
- total REAL
- city TEXT
- channel TEXT
- created_at TEXT (YYYY-MM-DD)
"""


_CODE_FENCE_RE = re.compile(r"^```(?:sql)?\s*|\s*```$", re.IGNORECASE)
_DISALLOWED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|PRAGMA|ATTACH|DETACH|VACUUM)\b",
    re.IGNORECASE,
)


def _strip_fences(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text).strip()


def sanitize_sql(sql: str) -> str:
    sql = _strip_fences(sql)
    match = re.search(r"(?is)\bselect\b.*?(?:;|$)", sql)
    if match:
        sql = match.group(0)
    sql = sql.strip().rstrip(";").strip()
    if not sql:
        raise ValueError("Empty SQL from LLM")
    if _DISALLOWED.search(sql):
        raise ValueError("LLM SQL contains a disallowed statement")
    if not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")
    return sql + ";"


def generate_sql(
    question: str,
    limit: Optional[int] = 15,
    model_name: str = "gemini-2.5-flash",
) -> str:
    if not is_gemini_configured():
        raise RuntimeError("Gemini not configured (missing API key)")

    model = build_gemini_model(model_name)
    limit_instruction = ""
    if limit:
        limit_instruction = f" Always include `LIMIT {int(limit)}`."

    prompt = f"""You generate SQL for a SQLite database.

{SCHEMA_HINT}

Task:
- Convert the user's question to ONE SQLite SELECT query over the orders table.
- Return ONLY the SQL query text, no markdown, no explanation.
- Use only the columns listed above.{limit_instruction}

User question:
{question}
"""

    response = model.generate_content(prompt)
    text = getattr(response, "text", "") or ""
    return sanitize_sql(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SQLite SELECT SQL from a natural-language question.")
    parser.add_argument("question", help="Natural language question")
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--model", default="gemini-2.5-flash")
    args = parser.parse_args()

    sql = generate_sql(args.question, limit=args.limit, model_name=args.model)
    print(sql)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
