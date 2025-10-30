import { useEffect, useState } from "react";
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
  val_score: number;
  trained_at: string;
  model_path: string;
  params: any;
};

export default function Models() {
  const [models, setModels] = useState<ModelMeta[]>([]);
  const [selected, setSelected] = useState<ModelMeta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [tickers, setTickers] = useState<string[]>([]);
  const [tickersToTrain, setTickersToTrain] = useState<string[]>([]);

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

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Trained Models</CardTitle>
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
          {error && <div className="p-4 bg-red-100 text-red-700 rounded">{error}</div>}
          <div className="overflow-x-auto mb-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Model ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Tickers</TableHead>
                  <TableHead>Target</TableHead>
                  <TableHead>Val Score</TableHead>
                  <TableHead>Trained At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {models.map((m) => (
                  <TableRow
                    key={m.model_id}
                    className="cursor-pointer"
                    onClick={() => handleRowClick(m.model_id)}
                  >
                    <TableCell className="font-mono">{m.model_id}</TableCell>
                    <TableCell>{m.model_type}</TableCell>
                    <TableCell>
                      {Array.isArray(m.tickers)
                        ? m.tickers.join(", ")
                        : m.tickers}
                    </TableCell>
                    <TableCell>{m.target}</TableCell>
                    <TableCell>{m.val_score?.toFixed(4)}</TableCell>
                    <TableCell>{m.trained_at?.substring(0, 19).replace("T", " ")}</TableCell>
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
