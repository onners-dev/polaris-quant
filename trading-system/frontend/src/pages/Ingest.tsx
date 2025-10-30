import { useAppStore } from "../store/useAppStore";
import { ingestYahooStock } from "../services/ingestApi";
import { useState } from "react";
import TickerAutocomplete from "../components/TickerAutocomplete";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Ingest() {
  const ticker = useAppStore((s) => s.ticker);
  const setTicker = useAppStore((s) => s.setTicker);

  const start = useAppStore((s) => s.start);
  const setStart = useAppStore((s) => s.setStart);
  const end = useAppStore((s) => s.end);
  const setEnd = useAppStore((s) => s.setEnd);

  const ingestResult = useAppStore((s) => s.ingestResult);
  const setIngestResult = useAppStore((s) => s.setIngestResult);

  const loading = useAppStore((s) => s.loading);
  const setLoading = useAppStore((s) => s.setLoading);

  const [error, setError] = useState<string | null>(null);

  async function handleIngest() {
    setLoading(true);
    setError(null);
    setIngestResult(null);
    try {
      const data = await ingestYahooStock([ticker], start, end);
      setIngestResult(data);
    } catch (e: any) {
      setError(e.message || "Error fetching data.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-lg mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Stock Data Ingestion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 mb-4">
            <TickerAutocomplete value={ticker} onChange={setTicker} />
            <Input
              type="date"
              value={start}
              onChange={e => setStart(e.target.value)}
              placeholder="Start Date"
            />
            <Input
              type="date"
              value={end}
              onChange={e => setEnd(e.target.value)}
              placeholder="End Date"
            />
            <Button
              onClick={handleIngest}
              disabled={!ticker || loading}
              className="w-full"
              size="lg"
            >
              {loading ? "Fetching..." : "Fetch Data"}
            </Button>
          </div>
          {ingestResult && (
            <div className="p-4 bg-green-100 rounded">
              <strong>Success!</strong>
              <pre className="text-xs">{JSON.stringify(ingestResult, null, 2)}</pre>
            </div>
          )}
          {error && (
            <div className="p-4 bg-red-100 rounded text-red-700">
              <strong>Error:</strong> {error}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
