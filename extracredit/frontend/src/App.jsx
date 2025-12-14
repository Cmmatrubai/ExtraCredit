import { useMemo, useState } from "react";

const mockResponse = {
  original_query: "Show me pending orders",
  generated_sql:
    "SELECT order_id, customer, status, total, city, channel, created_at FROM orders WHERE status = 'pending' ORDER BY created_at DESC LIMIT 15;",
  columns: ["order_id", "customer", "status", "total", "city", "channel", "created_at"],
  rows: [
    {
      order_id: 102,
      customer: "Bright Future",
      status: "pending",
      total: 980,
      city: "Chicago",
      channel: "mobile",
      created_at: "2024-10-05"
    },
    {
      order_id: 107,
      customer: "Summit Foods",
      status: "pending",
      total: 340.1,
      city: "Denver",
      channel: "web",
      created_at: "2024-10-08"
    }
  ],
  llm_output:
    'Your question: "Show me pending orders". Returned 2 rows; total amount $1,320.10. Status mix → pending: 2.',
  source: "mock"
};

function App() {
  const [question, setQuestion] = useState("");
  const [limit, setLimit] = useState(15);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });

  const sortedRows = useMemo(() => {
    if (!data?.rows || !sortConfig.key) return data?.rows || [];
    const rowsCopy = [...data.rows];
    rowsCopy.sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortConfig.direction === "asc" ? aVal - bVal : bVal - aVal;
      }
      return sortConfig.direction === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
    return rowsCopy;
  }, [data, sortConfig]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question, limit })
      });
      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || "Request failed");
      }
      const payload = await res.json();
      setData(payload);
    } catch (err) {
      console.error(err);
      setError("Backend not reachable; showing mock data instead.");
      setData(mockResponse);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (column) => {
    if (sortConfig.key === column) {
      setSortConfig({
        key: column,
        direction: sortConfig.direction === "asc" ? "desc" : "asc"
      });
    } else {
      setSortConfig({ key: column, direction: "asc" });
    }
  };

  const reset = () => {
    setData(null);
    setQuestion("");
    setError("");
    setSortConfig({ key: null, direction: "asc" });
  };

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="eyebrow">Extra Credit</p>
          <h1>NL → SQL Explorer</h1>
          <p className="sub">
            Type a natural-language request, see the generated SQL, results, and LLM narrative.
          </p>
        </div>
        <div className="status">
          <span className="dot" />
          <span>{data?.source ? `Backend: ${data.source}` : "Ready"}</span>
        </div>
      </header>

      <form className="card input-card" onSubmit={handleSubmit}>
        <label className="label">Natural language question</label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., Show pending web orders in New York over $500"
          required
        />
        <div className="controls">
          <label className="inline">
            Row limit
            <input
              type="number"
              min="1"
              max="500"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
            />
          </label>
          <div className="buttons">
            <button type="button" className="ghost" onClick={reset}>
              New query
            </button>
            <button type="submit" disabled={loading}>
              {loading ? "Running..." : "Run"}
            </button>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
      </form>

      {data && (
        <>
          <section className="grid">
            <div className="card">
              <h3>Original Query</h3>
              <p className="mono">{data.original_query}</p>
            </div>
            <div className="card">
              <h3>Generated SQL</h3>
              <pre className="code-block">{data.generated_sql}</pre>
            </div>
            <div className="card">
              <h3>LLM Output</h3>
              <p>{data.llm_output}</p>
            </div>
          </section>

          <section className="card table-card">
            <div className="table-header">
              <h3>Results</h3>
              <p className="hint">Click headers to sort</p>
            </div>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    {data.columns.map((col) => (
                      <th key={col} onClick={() => handleSort(col)}>
                        {col}
                        {sortConfig.key === col ? (
                          <span className="sort">{sortConfig.direction === "asc" ? "↑" : "↓"}</span>
                        ) : null}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.length === 0 && (
                    <tr>
                      <td colSpan={data.columns.length} className="empty">
                        No rows found.
                      </td>
                    </tr>
                  )}
                  {sortedRows.map((row, idx) => (
                    <tr key={idx}>
                      {data.columns.map((col) => (
                        <td key={col}>{String(row[col] ?? "")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default App;
