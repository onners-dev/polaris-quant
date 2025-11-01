import { useEffect, useState } from "react";
import { runBacktest, getBacktestResult, listBacktests } from "../services/backtestApi";
import { listModels } from "../services/modelsApi";
import { Card } from "../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function getMetricInterpretation(metrics: any) {
  if (!metrics) return "";
  const {
    total_return,
    sharpe,
    max_drawdown,
    cagr,
    volatility
  } = metrics;

  if (sharpe === undefined || total_return === undefined) return "";

  let summary = [];

  // Return summary
  if (total_return > 0.2)
    summary.push("Strong positive return.");
  else if (total_return > 0.05)
    summary.push("Modest gain over period.");
  else if (total_return < -0.2)
    summary.push("Significant loss in backtest.");
  else if (total_return < 0)
    summary.push("Small loss overall.");
  else
    summary.push("Flat/neutral performance.");

  // Sharpe summary
  if (sharpe > 2)
    summary.push("Excellent risk-adjusted performance (high Sharpe).");
  else if (sharpe > 1)
    summary.push("Good risk-adjusted performance.");
  else if (sharpe > 0.5)
    summary.push("Acceptable but can be improved.");
  else if (sharpe < 0)
    summary.push("Worse than holding cash (negative Sharpe).");
  else
    summary.push("Low risk-adjusted return (Sharpe ~0).");

  // Drawdown
  if (max_drawdown > 0.5)
    summary.push("⚠️ High risk: experienced deep drawdowns.");
  else if (max_drawdown > 0.3)
    summary.push("Moderate drawdowns.");

  // Volatility
  if (volatility && volatility > 0.5)
    summary.push("This system is highly volatile.");
  else if (volatility && volatility < 0.15)
    summary.push("Low or below-market volatility.");

  // CAGR
  if (cagr !== undefined) {
    if (cagr > 0.15)
      summary.push("Strong annualized growth (CAGR).");
    else if (cagr > 0)
      summary.push("Positive annualized growth.");
    else if (cagr < -0.10)
      summary.push("Annualized shrinkage/drift.");
  }

  if (summary.length === 0) {
    summary.push("No meaningful performance detected.");
  }
  return summary.join(" ");
}

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
            {backtestResult?.metrics && (
              <div className={`p-2 rounded mb-2 text-sm ${backtestResult.metrics.sharpe > 1 ? "bg-green-100 text-green-800" : backtestResult.metrics.sharpe < 0 ? "bg-red-100 text-red-800" : "bg-yellow-100 text-yellow-900"}`}>
                {getMetricInterpretation(backtestResult.metrics)}
              </div>
            )}
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
