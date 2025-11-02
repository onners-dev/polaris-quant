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
// Add Recharts for visuals
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList
} from "recharts";

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
  features_hash_train?: string;
  params?: any;
  features?: string[];
  feature_importances?: number[];
  cv_results?: any[];
  [key: string]: any;
};

type LatestHashMap = { [modelId: string]: string };

async function fetchLatestHashForModel(model: ModelMeta): Promise<[string, string]> {
  const tickers = Array.isArray(model.tickers) ? model.tickers : [model.tickers];
  const params = new URLSearchParams();
  tickers.forEach(t => params.append("tickers", t));
  params.append("target", model.target || "Return_1d");
  const res = await fetch(`/api/data/latest-hash?${params}`).then(r => r.json());
  return [model.model_id, res.features_hash];
}

function mean(arr: number[]) {
  if (!Array.isArray(arr) || arr.length === 0) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function round(n: number | undefined, d = 4) {
  return n === undefined ? "-" : n.toFixed(d);
}

function FeatureImportanceChart({ features, importances }: { features: string[], importances: number[] }) {
  const chartData = features.map((f, i) => ({
    feature: f,
    importance: importances[i] || 0,
  }))
  .sort((a, b) => b.importance - a.importance)
  .slice(0, 12); // Top 12

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} layout="vertical" margin={{left: 16, right: 16, top: 8, bottom: 8}}>
        <XAxis type="number" />
        <YAxis type="category" dataKey="feature" width={110} />
        <Tooltip />
        <Bar dataKey="importance" fill="#34d399">
          <LabelList dataKey="importance" position="right" formatter={v => v.toFixed(3)} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function ModelDetail({ model }: { model: ModelMeta }) {
  if (!model) return null;
  const { model_id, tickers, target, trained_at, params, features = [], feature_importances = [], cv_results = [] } = model;

  // Find best cv run (lowest mean val_rmse across folds)
  let bestCfg, bestMetrics: any[] = [];
  let bestScore = Infinity;

  if (Array.isArray(cv_results)) {
    for (const r of cv_results) {
      const metrics = r.metrics || [];
      const mscore = mean(metrics.map(f => f.val_rmse));
      if (mscore < bestScore) {
        bestScore = mscore;
        bestCfg = r.cfg;
        bestMetrics = metrics;
      }
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-muted rounded p-4 mb-2 flex flex-col sm:flex-row gap-8">
        <div>
          <div className="font-semibold">Model ID:</div>
          <div className="font-mono text-xs truncate mb-1">{model_id}</div>
          <div><span className="font-semibold">Tickers:</span> {Array.isArray(tickers) ? tickers.join(", ") : tickers}</div>
          <div><span className="font-semibold">Target:</span> {target}</div>
          <div><span className="font-semibold">Trained At:</span> {trained_at?.substring(0, 19).replace("T", " ")}</div>
        </div>
        <div>
          <div className="font-semibold">Best Params:</div>
          <pre className="text-xs">{JSON.stringify(params || bestCfg, null, 2)}</pre>
        </div>
      </div>
      <div>
        <div className="font-semibold mb-1">Feature Importances:</div>
        {features?.length && feature_importances?.length ? (
          <FeatureImportanceChart features={features} importances={feature_importances} />
        ) : (
          <div className="text-sm text-gray-500">No feature importances recorded.</div>
        )}
      </div>
      <div>
        <div className="font-semibold mb-1">Cross-Validation Results:</div>
        {Array.isArray(cv_results) && cv_results.length ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Config</TableHead>
                  {[...Array(cv_results[0].metrics.length).keys()].map((fold) =>
                    <TableHead key={fold}>Fold {fold + 1} (Val/Test)</TableHead>
                  )}
                  <TableHead>Mean Val RMSE</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cv_results.map((r, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <pre className="text-xs">{JSON.stringify(r.cfg, null, 1)}</pre>
                    </TableCell>
                    {r.metrics.map((m: any, j: number) =>
                      <TableCell key={j} className="text-xs">
                        <div>Val RMSE: {round(m.val_rmse, 5)}</div>
                        <div>Val Sharpe: {round(m.val_sharpe)}</div>
                        <div>Test RMSE: {round(m.test_rmse, 5)}</div>
                        <div>Test Sharpe: {round(m.test_sharpe)}</div>
                      </TableCell>
                    )}
                    <TableCell>
                      {round(mean(r.metrics.map((m: any) => m.val_rmse)), 5)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-sm text-gray-500">No CV history available for this model.</div>
        )}
      </div>
    </div>
  );
}

export default function Models() {
  const [models, setModels] = useState<ModelMeta[]>([]);
  const [selected, setSelected] = useState<ModelMeta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tickers, setTickers] = useState<string[]>([]);
  const [tickersToTrain, setTickersToTrain] = useState<string[]>([]);
  const [filterTicker, setFilterTicker] = useState<string>("");
  const [latestHashes, setLatestHashes] = useState<LatestHashMap>({});

  useEffect(() => {
    setLoading(true);
    Promise.all([listModels(), getAvailableData()])
      .then(async ([modelData, tickersData]) => {
        setModels(Array.isArray(modelData) ? modelData : []);
        setTickers(Array.isArray(tickersData) ? tickersData.map((d: any) => d.ticker) : []);
        if (Array.isArray(modelData)) {
          const entries = await Promise.all(modelData.map(fetchLatestHashForModel));
          const hashes: LatestHashMap = {};
          entries.forEach(([mid, hash]) => { hashes[mid] = hash; });
          setLatestHashes(hashes);
        }
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
                      {latestHashes[m.model_id] && m.features_hash_train && latestHashes[m.model_id] !== m.features_hash_train && (
                        <span className="ml-2 px-2 py-0.5 text-xs rounded bg-orange-100 text-orange-900">
                          Data Drift
                        </span>
                      )}
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

          {!!selected && (
            <Card>
              <CardHeader>
                <CardTitle>Model Details</CardTitle>
              </CardHeader>
              <CardContent>
                <ModelDetail model={selected} />
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
