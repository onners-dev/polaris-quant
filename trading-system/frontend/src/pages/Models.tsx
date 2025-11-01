import { useEffect, useState, useMemo } from "react";
import { listModels, getModelDetails } from "../services/modelsApi";
import { trainModel } from "../services/modelsTrainApi";
import { getAvailableData } from "../services/dataApi";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";

type ModelMeta = {
  model_id: string;
  model_type: string;
  tickers: string[] | string;
  target: string;
  val_score?: number;
  val_sharpe?: number;
  val_rmse?: number;
  test_sharpe?: number;
  test_rmse?: number;
  test_drawdown?: number;
  trained_at?: string;
  model_path?: string;
  params?: any;
  [key: string]: any;
};

export default function Models() {
  const [models, setModels] = useState<ModelMeta[]>([]);
  const [selected, setSelected] = useState<ModelMeta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [tickers, setTickers] = useState<string[]>([]);
  const [tickersToTrain, setTickersToTrain] = useState<string[]>([]);
  const [filterTicker, setFilterTicker] = useState<string>("");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listModels(),
      getAvailableData()
    ]).then(([modelData, tickersData]) => {
      setModels(Array.isArray(modelData) ? modelData : []);
      setTickers(Array.isArray(tickersData) ? tickersData.map((d: any) => d.ticker) : []);
    })
    .catch(e => setError(e.message || "Failed to load models/tickers"))
    .finally(() => setLoading(false));
  }, []);

  async function handleTrain() {
    if (!tickersToTrain.length) return;
    setLoading(true);
    setError(null);
    try {
      const result = await trainModel(tickersToTrain);
      setModels(m => [...m, result.model]);
    } catch (e: any) {
      setError(e.message || "Failed to train model");
    }
    setLoading(false);
  }

  async function handleRowClick(model_id: string) {
    setSelected(null);
    setLoading(true);
    try {
      const meta = await getModelDetails(model_id);
      setSelected(meta);
    } catch (e: any) {
      setError(e.message || "Failed to get model details");
      setSelected(null);
    }
    setLoading(false);
  }

  function handleTickerChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const selectedOptions = Array.from(e.target.selectedOptions).map(opt => opt.value);
    setTickersToTrain(selectedOptions);
  }

  // New: Filtering and Sorting
  const filteredLeaderboard = useMemo(() => {
    let filtered = models;
    if (filterTicker) {
      filtered = filtered.filter(m => {
        if (Array.isArray(m.tickers)) {
          return m.tickers.map(t => t.toUpperCase()).includes(filterTicker.toUpperCase());
        }
        return String(m.tickers).toUpperCase() === filterTicker.toUpperCase();
      });
    }
    // Sort by test_sharpe descending, then test_rmse ascending
    return filtered
      .slice()
      .sort((a, b) => (Number(b.test_sharpe || 0) - Number(a.test_sharpe || 0)) ||
                      (Number(a.test_rmse || Infinity) - Number(b.test_rmse || Infinity))
      );
  }, [models, filterTicker]);

  const championId = filteredLeaderboard.length > 0 ? filteredLeaderboard[0].model_id : null;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Model Leaderboard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 items-center mb-4">
            <select
              className="border rounded px-2 py-1"
              multiple
              style={{ minWidth: 150, height: 42 }}
              value={tickersToTrain}
              onChange={handleTickerChange}
            >
              {tickers.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <Button
              onClick={handleTrain}
              disabled={!tickersToTrain.length || loading}
              className="h-10"
            >
              Train Model
            </Button>
            <span className="text-sm text-gray-600">
              (Select one or more tickers. Hold Cmd/Ctrl for multi-select)
            </span>
            {loading && <span>Working...</span>}
          </div>

          {/* New: Filter bar */}
          <div className="mb-2 flex gap-4 items-center">
            <label htmlFor="filterTicker" className="text-sm">Filter by ticker:</label>
            <select
              id="filterTicker"
              className="border rounded px-2 py-1"
              value={filterTicker}
              onChange={e => setFilterTicker(e.target.value)}
            >
              <option value="">All</option>
              {tickers.map(t =>
                <option key={t} value={t}>{t}</option>
              )}
            </select>
          </div>

          {error && <div className="p-4 bg-red-100 text-red-700 rounded">{error}</div>}

          <div className="overflow-x-auto mb-6">
            <Table className="min-w-[900px]">
              <TableHeader>
                <TableRow>
                  <TableHead>Model ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Tickers</TableHead>
                  <TableHead>Target</TableHead>
                  <TableHead>Test Sharpe</TableHead>
                  <TableHead>Test RMSE</TableHead>
                  <TableHead>Test MaxDD</TableHead>
                  <TableHead>Trained At</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLeaderboard.map((m) => (
                  <TableRow
                    key={m.model_id}
                    className={`cursor-pointer hover:bg-muted transition 
                               ${championId === m.model_id ? "border-l-4 border-green-500 font-semibold bg-green-50 dark:bg-green-950" : ""}`}
                    onClick={() => handleRowClick(m.model_id)}
                    title={championId === m.model_id ? "Champion Model" : ""}
                  >
                    <TableCell className="font-mono text-xs">{m.model_id.slice(0, 16)}</TableCell>
                    <TableCell>{m.model_type}</TableCell>
                    <TableCell>
                      {Array.isArray(m.tickers)
                        ? m.tickers.join(", ")
                        : m.tickers}
                    </TableCell>
                    <TableCell>{m.target}</TableCell>
                    <TableCell>{m.test_sharpe !== undefined ? m.test_sharpe.toFixed(4) : "-"}</TableCell>
                    <TableCell>{m.test_rmse !== undefined ? m.test_rmse.toFixed(5) : "-"}</TableCell>
                    <TableCell>{m.test_drawdown !== undefined ? m.test_drawdown.toFixed(3) : "-"}</TableCell>
                    <TableCell>{m.trained_at?.substring(0, 19).replace("T", " ")}</TableCell>
                    <TableCell>
                      {championId === m.model_id &&
                        <span className="text-xs text-green-700 bg-green-200 rounded px-2 py-0.5">Champion</span>
                      }
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {selected && (
            <Card>
              <CardHeader>
                <CardTitle>Model Details</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs overflow-x-auto">{JSON.stringify(selected, null, 2)}</pre>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
