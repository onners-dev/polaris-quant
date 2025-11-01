import { useEffect, useState } from "react";
import { runBacktest, getBacktestResult, listBacktests } from "../services/backtestApi";
import { listModels } from "../services/modelsApi";
import { Card } from "../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Backtesting() {
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [backtestResult, setBacktestResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listModels().then(setModels);
    loadHistory();
  }, []);

  function loadHistory() {
    setLoading(true);
    listBacktests(selectedModel || undefined).then(setHistory).finally(() => setLoading(false));
  }

  async function handleRunBacktest() {
    if (!selectedModel) return;
    setLoading(true);
    setError(null);
    try {
      const result = await runBacktest({ model_id: selectedModel });
      setBacktestResult(result.result || result);
      loadHistory();
    } catch (e: any) {
      setError(e.message || "Backtest failed");
    }
    setLoading(false);
  }

  async function handleRowClick(run_id: string) {
    setLoading(true);
    try {
      const detail = await getBacktestResult(run_id);
      setBacktestResult(detail);
    } catch (e: any) {
      setError(e.message || "Could not load backtest");
    }
    setLoading(false);
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 p-8">
      <Card>
        <div className="flex flex-col gap-4">
          <label>
            <span className="font-medium mr-2">Model:</span>
            <select
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
              className="border px-2 py-1 rounded"
            >
              <option value="">Select model</option>
              {models.map(m => <option value={m.model_id} key={m.model_id}>{m.model_id}</option>)}
            </select>
            <button className="ml-4 px-3 py-1 bg-blue-600 text-white rounded" onClick={handleRunBacktest} disabled={loading || !selectedModel}>
              Run Backtest
            </button>
          </label>
        </div>
      </Card>

      {error && <div className="text-red-600">{error}</div>}

      {backtestResult && (
        <Card>
          <div className="mb-2 space-y-2">
            <div className="font-semibold">Metrics</div>
            <pre className="text-xs bg-neutral-100 rounded p-2 overflow-auto">{JSON.stringify(backtestResult.metrics, null, 2)}</pre>
            <div className="font-semibold mt-4">Equity Curve</div>
            <div style={{ width: "100%", height: 200 }}>
              <ResponsiveContainer>
                <LineChart data={Object.entries(backtestResult.equity_curve).map(([Date, value]) => ({ Date, value }))}>
                  <XAxis dataKey="Date" minTickGap={20} />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
      )}

      <Card>
        <div className="font-semibold mb-2">Backtest History</div>
        <div className="max-h-64 overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Run ID</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Period</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Sharpe</TableHead>
                <TableHead>Return</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6}>No runs</TableCell>
                </TableRow>
              )}
              {history.map((row: any) => (
                <TableRow key={row.run_id} onClick={() => handleRowClick(row.run_id)} style={{ cursor: "pointer" }}>
                  <TableCell className="truncate max-w-[14ch]">{row.run_id}</TableCell>
                  <TableCell>{row.model_id}</TableCell>
                  <TableCell>
                    {row.start_date?.slice(0,10)} - {row.end_date?.slice(0,10)}
                  </TableCell>
                  <TableCell>{row.created_at?.split("T")[0]}</TableCell>
                  <TableCell>{row.metrics?.sharpe?.toFixed(2)}</TableCell>
                  <TableCell>{((row.metrics?.total_return ?? 0) * 100).toFixed(1)}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}
