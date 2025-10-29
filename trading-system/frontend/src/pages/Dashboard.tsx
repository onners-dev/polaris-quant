import { useAppStore } from "../store/useAppStore";
import { ingestYahooStock } from "../services/ingestApi";
import { useState } from "react";

export default function Dashboard() {
  const ticker = useAppStore((s) => s.ticker);
  const setTicker = useAppStore((s) => s.setTicker);

  const start = useAppStore((s) => s.start);
  const setStart = useAppStore((s) => s.setStart);
  const end = useAppStore((s) => s.end);
  const setEnd = useAppStore((s) => s.setEnd);

  const ingestResult = useAppStore((s) => s.ingestResult);
  const setIngestResult = useAppStore((s) => s.setIngestResult);

  const loading = useAppStore((s) => s.loading);
  const setLoading = useAppStore((s) => s.setLoading);

  const [error, setError] = useState<string | null>(null);

  async function handleIngest() {
    setLoading(true);
    setError(null);
    setIngestResult(null);
    try {
      const data = await ingestYahooStock([ticker], start, end);
      setIngestResult(data);
    } catch (e: any) {
      setError(e.message || "Error fetching data.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Stock Data Ingestion</h2>
      <div className="flex flex-col gap-4 mb-4">
        <input
          className="border rounded px-3 py-2"
          placeholder="Stock Ticker (e.g. AAPL)"
          value={ticker}
          onChange={e => setTicker(e.target.value.toUpperCase())}
        />
        <input
          className="border rounded px-3 py-2"
          type="date"
          value={start}
          onChange={e => setStart(e.target.value)}
        />
        <input
          className="border rounded px-3 py-2"
          type="date"
          value={end}
          onChange={e => setEnd(e.target.value)}
        />
        <button
          onClick={handleIngest}
          className="bg-blue-600 text-white py-2 rounded disabled:opacity-60"
          disabled={!ticker || loading}
        >
          {loading ? "Fetching..." : "Fetch Data"}
        </button>
      </div>
      {ingestResult && (
        <div className="p-4 bg-green-100 rounded">
          <strong>Success!</strong>
          <pre className="text-xs">{JSON.stringify(ingestResult, null, 2)}</pre>
        </div>
      )}
      {error && (
        <div className="p-4 bg-red-100 rounded text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}
