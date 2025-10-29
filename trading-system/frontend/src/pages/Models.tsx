import { useEffect, useState } from "react";
import { listModels, getModelDetails } from "../services/modelsApi";

type ModelMeta = {
  model_id: string;
  ticker: string;
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

  useEffect(() => {
    setLoading(true);
    listModels()
      .then(data => setModels(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message || "Failed to load models"))
      .finally(() => setLoading(false));
  }, []);

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

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Trained Models</h2>
      {loading && <p>Loading...</p>}
      {error && <div className="p-4 bg-red-100 text-red-700">{error}</div>}
      <div className="overflow-x-auto mb-6">
        <table className="min-w-full bg-white border rounded shadow">
          <thead>
            <tr>
              <th className="px-4 py-2 border-b">Model ID</th>
              <th className="px-4 py-2 border-b">Ticker</th>
              <th className="px-4 py-2 border-b">Target</th>
              <th className="px-4 py-2 border-b">Val Score</th>
              <th className="px-4 py-2 border-b">Trained At</th>
            </tr>
          </thead>
          <tbody>
            {models.map((m) => (
              <tr
                key={m.model_id}
                className="hover:bg-blue-50 cursor-pointer"
                onClick={() => handleRowClick(m.model_id)}
              >
                <td className="px-4 py-2 border-b font-mono">{m.model_id}</td>
                <td className="px-4 py-2 border-b">{m.ticker}</td>
                <td className="px-4 py-2 border-b">{m.target}</td>
                <td className="px-4 py-2 border-b">{m.val_score?.toFixed(4)}</td>
                <td className="px-4 py-2 border-b">{m.trained_at?.substring(0, 19).replace("T", " ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selected && (
        <div className="bg-gray-100 p-4 rounded shadow">
          <h3 className="text-lg font-bold mb-2">Model Details</h3>
          <pre className="text-xs overflow-x-auto">{JSON.stringify(selected, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
