import { useEffect, useState } from "react";
import { getAvailableData } from "../services/dataApi";
import { getTableData } from "../services/tableDataApi";
import { cleanData } from "../services/cleanApi";
import { generateFeatures } from "../services/featuresApi";

type TickerData = {
  ticker: string;
  start_date: string;
  end_date: string;
  row_count: number;
};

const TABLE_OPTIONS = [
  { label: "Raw", value: "raw" },
  { label: "Cleaned", value: "cleaned" },
  { label: "Features", value: "features" },
];

export default function DataViewer() {
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<"raw" | "cleaned" | "features">("raw");
  const [tableData, setTableData] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  function loadData() {
    setLoading(true);
    getAvailableData()
      .then((data) => {
        if (Array.isArray(data)) setTickers(data);
        else setTickers([]);
      })
      .catch((e) => setError(e.message || "Error fetching data"))
      .finally(() => setLoading(false));
  }

  async function handleClean() {
    setActionStatus("Cleaning...");
    try {
      await cleanData();
      setActionStatus("Cleaned!");
      loadData();
    } catch (e: any) {
      setActionStatus("Cleaning failed: " + (e.message || e));
    }
  }

  async function handleFeatures() {
    setActionStatus("Extracting features...");
    try {
      await generateFeatures();
      setActionStatus("Features generated!");
    } catch (e: any) {
      setActionStatus("Feature extraction failed: " + (e.message || e));
    }
  }

  async function handleViewDetails(ticker: string) {
    setSelectedTicker(ticker);
    setTableData([]);
    setActionStatus("Loading data...");
    try {
      const data = await getTableData(selectedTable, ticker);
      setTableData(Array.isArray(data) ? data : []);
      setActionStatus(null);
    } catch (e: any) {
      setActionStatus("Failed to load data: " + (e.message || e));
      setTableData([]);
    }
  }

  useEffect(() => {
    // When changing table or ticker, fetch data again
    if (selectedTicker) {
      handleViewDetails(selectedTicker);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTable, selectedTicker]);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-6">Available Data</h2>
      <div className="flex gap-4 mb-4">
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={handleClean}
          disabled={loading}
        >
          Clean Data
        </button>
        <button
          className="bg-green-700 text-white px-4 py-2 rounded"
          onClick={handleFeatures}
          disabled={loading}
        >
          Generate Features
        </button>
        {actionStatus && <span>{actionStatus}</span>}
      </div>
      {loading && <p>Loading...</p>}
      {error && <div className="p-4 bg-red-100 text-red-700">{error}</div>}
      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="table-auto w-full text-left border rounded bg-white mb-6">
            <thead>
              <tr>
                <th className="px-4 py-2 border-b">Ticker</th>
                <th className="px-4 py-2 border-b">Start Date</th>
                <th className="px-4 py-2 border-b">End Date</th>
                <th className="px-4 py-2 border-b">Rows</th>
                <th className="px-4 py-2 border-b">Actions</th>
              </tr>
            </thead>
            <tbody>
              {Array.isArray(tickers) &&
                tickers.map((row) => (
                  <tr key={row.ticker}>
                    <td className="px-4 py-2 border-b font-mono">{row.ticker}</td>
                    <td className="px-4 py-2 border-b">{row.start_date?.substring(0, 10)}</td>
                    <td className="px-4 py-2 border-b">{row.end_date?.substring(0, 10)}</td>
                    <td className="px-4 py-2 border-b">{row.row_count}</td>
                    <td className="px-4 py-2 border-b">
                      <button
                        className="bg-gray-200 hover:bg-gray-300 rounded px-3 py-1"
                        onClick={() => setSelectedTicker(row.ticker)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {selectedTicker && (
            <div className="mt-6 bg-gray-100 rounded p-4">
              <h3 className="font-bold text-lg mb-2 flex items-center gap-4">
                Details for {selectedTicker}
                <select
                  value={selectedTable}
                  onChange={e => setSelectedTable(e.target.value as any)}
                  className="text-base bg-white px-2 py-1 rounded border ml-auto"
                >
                  {TABLE_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </h3>
              {actionStatus && <span>{actionStatus}</span>}
              {!actionStatus && tableData.length === 0 && (
                <span>No data found for this table/ticker.</span>
              )}
              {!actionStatus && tableData.length > 0 && (
                <pre className="overflow-x-auto text-xs bg-gray-50 rounded p-2">
                  {JSON.stringify(tableData.slice(0, 10), null, 2)} {/* Display sample */}
                </pre>
              )}
              {/* Here you can add tabs, charts etc in the future */}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
