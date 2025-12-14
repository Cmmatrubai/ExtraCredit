from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from gemini_client import build_gemini_model, is_gemini_configured


def _summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = 0.0
    status_counts: Dict[str, int] = {}
    for row in rows:
        try:
            total += float(row.get("total", 0) or 0)
        except (TypeError, ValueError):
            pass
        status = str(row.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
    return {"row_count": len(rows), "total_sum": total, "status_counts": status_counts}


def generate_answer(
    question: str,
    sql: str,
    rows: List[Dict[str, Any]],
    model_name: str = "gemini-2.5-flash",
) -> str:
    if not is_gemini_configured():
        raise RuntimeError("Gemini not configured (missing API key)")

    model = build_gemini_model(model_name)
    summary = _summarize_rows(rows)

    prompt = f"""You are helping answer a database question.

User question:
{question}

SQL that was executed:
{sql}

Result summary (not full rows):
{json.dumps(summary)}

Write a concise, helpful response (2-5 sentences) describing what the results show.
Do not mention that you are an AI model. Do not mention JSON.
"""
    response = model.generate_content(prompt)
    return (getattr(response, "text", "") or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a narrative answer using Gemini.")
    parser.add_argument("question")
    parser.add_argument("sql")
    parser.add_argument("--rows-json", required=True, help="JSON array of row objects")
    parser.add_argument("--model", default="gemini-2.5-flash")
    args = parser.parse_args()

    rows = json.loads(args.rows_json)
    if not isinstance(rows, list):
        raise SystemExit("--rows-json must be a JSON array")

    print(generate_answer(args.question, args.sql, rows, model_name=args.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
