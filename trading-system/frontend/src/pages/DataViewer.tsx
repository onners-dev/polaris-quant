import { useEffect, useState } from "react";
import { getAvailableData } from "../services/dataApi";
import { getTableData } from "../services/tableDataApi";
import { cleanData } from "../services/cleanApi";
import { generateFeatures } from "../services/featuresApi";
import TickerName from "../components/TickerName";
import { useTickerMeta } from "../hooks/useTickerMeta";

type TableInfo = {
  start_date?: string;
  end_date?: string;
  row_count?: number;
};

type TickerData = {
  ticker: string;
  raw?: TableInfo;
  cleaned?: TableInfo;
  features?: TableInfo;
};

const TABLE_OPTIONS = [
  { label: "Raw", value: "raw" },
  { label: "Cleaned", value: "cleaned" },
  { label: "Features", value: "features" },
];

export default function DataViewer() {
  const [meta] = useTickerMeta();
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
      loadData();
    } catch (e: any) {
      setActionStatus("Feature extraction failed: " + (e.message || e));
    }
  }

  async function handleViewDetails(ticker: string, table: "raw" | "cleaned" | "features") {
    setSelectedTicker(ticker);
    setSelectedTable(table);
    setTableData([]);
    setActionStatus("Loading data...");
    try {
      const data = await getTableData(table, ticker);
      setTableData(Array.isArray(data) ? data : []);
      setActionStatus(null);
    } catch (e: any) {
      setActionStatus("Failed to load data: " + (e.message || e));
      setTableData([]);
    }
  }

  useEffect(() => {
    if (selectedTicker && selectedTable) {
      handleViewDetails(selectedTicker, selectedTable);
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
                <th className="px-4 py-2 border-b">Company</th>
                <th className="px-4 py-2 border-b">Raw</th>
                <th className="px-4 py-2 border-b">Cleaned</th>
                <th className="px-4 py-2 border-b">Features</th>
                <th className="px-4 py-2 border-b">Actions</th>
              </tr>
            </thead>
            <tbody>
              {Array.isArray(tickers) &&
                tickers.map((row) => (
                  <tr key={row.ticker}>
                    <td className="px-4 py-2 border-b font-mono">{row.ticker}</td>
                    <td className="px-4 py-2 border-b">
                      <TickerName ticker={row.ticker} />
                    </td>
                    <td className="px-4 py-2 border-b">
                      {row.raw
                        ? `${row.raw.start_date?.substring(0, 10) || ""}—${row.raw.end_date?.substring(0, 10) || ""} (${row.raw.row_count})`
                        : <span className="text-gray-400">None</span>}
                    </td>
                    <td className="px-4 py-2 border-b">
                      {row.cleaned
                        ? `${row.cleaned.start_date?.substring(0, 10) || ""}—${row.cleaned.end_date?.substring(0, 10) || ""} (${row.cleaned.row_count})`
                        : <span className="text-gray-400">None</span>}
                    </td>
                    <td className="px-4 py-2 border-b">
                      {row.features
                        ? `${row.features.start_date?.substring(0, 10) || ""}—${row.features.end_date?.substring(0, 10) || ""} (${row.features.row_count})`
                        : <span className="text-gray-400">None</span>}
                    </td>
                    <td className="px-4 py-2 border-b">
                      {TABLE_OPTIONS.map(opt => (
                        <button
                          key={opt.value}
                          className={
                            ((row as any)[opt.value])
                              ? "bg-gray-200 hover:bg-gray-300 rounded px-3 py-1 mr-1"
                              : "bg-gray-100 rounded px-3 py-1 mr-1 opacity-50 cursor-not-allowed"
                          }
                          disabled={!(row as any)[opt.value]}
                          onClick={() => {
                            if ((row as any)[opt.value]) {
                              setSelectedTicker(row.ticker);
                              setSelectedTable(opt.value as any);
                            }
                          }}
                        >View {opt.label}</button>
                      ))}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {selectedTicker && (
            <div className="mt-6 bg-gray-100 rounded p-4">
              <h3 className="font-bold text-lg mb-2 flex items-center gap-4">
                Details for {selectedTicker}: {TABLE_OPTIONS.find(opt => opt.value === selectedTable)?.label}
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
            </div>
          )}
        </div>
      )}
    </div>
  );
}
