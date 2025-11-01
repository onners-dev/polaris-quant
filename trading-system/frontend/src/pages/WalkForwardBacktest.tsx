import { useEffect, useState } from "react";
import { listModels } from "../services/modelsApi";
import { runWalkForward } from "../services/walkforwardApi";
import type { WalkForwardParams } from "../services/walkforwardApi";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Button } from "@/components/ui/button";


function getSplitLabel(split: any, i: number) {
  return split?.test_period ? `${split.test_period[0]} – ${split.test_period[1]}` : `Split ${i+1}`;
}

export default function WalkForwardBacktest() {
  const [models, setModels] = useState<any[]>([]);
  const [params, setParams] = useState<WalkForwardParams>({
    model_id: "",
    full_start: "",
    full_end: "",
    window_train: 252*2,
    window_test: 63,
    stride: 63,
    transaction_cost_bps: 1,
    slippage_bps: 0
  });
  const [splits, setSplits] = useState<any[]>([]);
  const [summary, setSummary] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listModels().then(setModels);
  }, []);

  async function handleRun() {
    setLoading(true);
    setError(null);
    setSplits([]);
    setSummary(null);
    try {
      const result = await runWalkForward(params);
      setSplits(result.splits || []);
      setSummary(result.summary || {});
    } catch (e: any) {
      setError(e.message || "Walk-forward backtest failed");
    }
    setLoading(false);
  }

  // Join all splits' equity curves for plotting overlay
  const equityCurves = splits.map((split, i) =>
    Object.entries(split.equity_curve || {}).map(([Date, value]) => ({
      Date,
      value,
      split: getSplitLabel(split, i)
    }))
  );

  // Concatenate curves for combined chart
  const allCurvePoints = equityCurves.flat();

  return (
    <div className="max-w-5xl mx-auto space-y-8 p-8">
      <Card>
        <CardHeader>
          <CardTitle>Walk-Forward Backtest</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4 items-end mb-2">
            <label className="flex flex-col text-xs font-semibold">
              Model
              <select
                className="border px-2 py-1 rounded"
                value={params.model_id}
                onChange={e => setParams(p => ({ ...p, model_id: e.target.value }))}
              >
                <option value="">Select Model</option>
                {models.map(m => (
                  <option key={m.model_id} value={m.model_id}>{m.model_id}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-xs">
              Start Date
              <input
                type="date"
                className="border px-2 py-1 rounded"
                value={params.full_start}
                onChange={e => setParams(p => ({ ...p, full_start: e.target.value }))}
              />
            </label>
            <label className="flex flex-col text-xs">
              End Date
              <input
                type="date"
                className="border px-2 py-1 rounded"
                value={params.full_end}
                onChange={e => setParams(p => ({ ...p, full_end: e.target.value }))}
              />
            </label>
            <label className="flex flex-col text-xs">
              Train Window (days)
              <input
                type="number"
                className="border px-2 py-1 rounded w-24"
                value={params.window_train}
                min={30} max={2000}
                onChange={e => setParams(p => ({ ...p, window_train: parseInt(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col text-xs">
              Test Window (days)
              <input
                type="number"
                className="border px-2 py-1 rounded w-20"
                value={params.window_test}
                min={10} max={500}
                onChange={e => setParams(p => ({ ...p, window_test: parseInt(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col text-xs">
              Stride (days)
              <input
                type="number"
                className="border px-2 py-1 rounded w-20"
                value={params.stride}
                min={1} max={500}
                onChange={e => setParams(p => ({ ...p, stride: parseInt(e.target.value) }))}
              />
            </label>
            <Button onClick={handleRun} disabled={loading || !params.model_id || !params.full_start || !params.full_end}>
              {loading ? "Running..." : "Run Walk-Forward"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <div className="text-red-600 p-2 bg-red-50 rounded">{error}</div>}

      {summary && (
        <Card>
          <CardHeader>
            <CardTitle>Walk-Forward Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              {Object.entries(summary).map(([k, v]) =>
                <div key={k}><span className="font-semibold">{k}:</span> {typeof v === "number" ? v.toFixed(4) : String(v)}</div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {splits.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Split-by-Split Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto mb-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Split</TableHead>
                    <TableHead>Test Period</TableHead>
                    <TableHead>Sharpe</TableHead>
                    <TableHead>Return</TableHead>
                    <TableHead>Drawdown</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {splits.map((split: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell>{i + 1}</TableCell>
                      <TableCell>{getSplitLabel(split, i)}</TableCell>
                      <TableCell>{split.metrics?.sharpe?.toFixed(3)}</TableCell>
                      <TableCell>{(split.metrics?.total_return * 100).toFixed(2)}%</TableCell>
                      <TableCell>{(split.metrics?.max_drawdown * 100).toFixed(2)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div>
              <div className="font-semibold">Equity Curves (All Splits Overlaid)</div>
              <div style={{ width: "100%", height: 320 }}>
                <ResponsiveContainer>
                  <LineChart data={allCurvePoints}>
                    <XAxis dataKey="Date" minTickGap={20} />
                    <YAxis />
                    <Tooltip />
                    {equityCurves.map((curve, i) => (
                      <Line
                        type="monotone"
                        dataKey="value"
                        data={curve}
                        key={i}
                        stroke={`hsl(${i * 58 % 360}, 70%, 50%)`}
                        dot={false}
                        strokeWidth={i === 0 ? 2 : 1}
                        name={`Split ${i + 1}`}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
