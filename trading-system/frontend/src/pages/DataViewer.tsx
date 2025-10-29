import { useEffect, useState } from "react";
import { getAvailableData } from "../services/dataApi";

type TickerData = {
  ticker: string;
  start_date: string;
  end_date: string;
  row_count: number;
};

export default function DataViewer() {
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getAvailableData()
      .then(setTickers)
      .catch((e) => setError(e.message || "Error fetching data"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-6">Available Data</h2>
      {loading && <p>Loading...</p>}
      {error && <div className="p-4 bg-red-100 text-red-700">{error}</div>}
      {!loading && !error && (
        <>
          {tickers.length === 0 ? (
            <p>No ingested data found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="table-auto w-full text-left border rounded bg-white">
                <thead>
                  <tr>
                    <th className="px-4 py-2 border-b">Ticker</th>
                    <th className="px-4 py-2 border-b">Start Date</th>
                    <th className="px-4 py-2 border-b">End Date</th>
                    <th className="px-4 py-2 border-b">Rows</th>
                  </tr>
                </thead>
                <tbody>
                  {tickers.map((row) => (
                    <tr key={row.ticker}>
                      <td className="px-4 py-2 border-b font-mono">{row.ticker}</td>
                      <td className="px-4 py-2 border-b">{row.start_date.substring(0, 10)}</td>
                      <td className="px-4 py-2 border-b">{row.end_date.substring(0, 10)}</td>
                      <td className="px-4 py-2 border-b">{row.row_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
