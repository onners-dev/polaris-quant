import { useEffect, useState } from "react";
import { getAvailableData } from "../services/dataApi";
import { getTableData } from "../services/tableDataApi";
import { cleanData } from "../services/cleanApi";
import { generateFeatures } from "../services/featuresApi";
import TickerName from "../components/TickerName";
import { useTickerMeta } from "../hooks/useTickerMeta";
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
      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        <Button onClick={handleClean} disabled={loading} variant="default">
          Clean Data
        </Button>
        <Button onClick={handleFeatures} disabled={loading} variant="default">
          Generate Features
        </Button>
        {actionStatus && <span className="my-auto">{actionStatus}</span>}
      </div>
      {loading && <p>Loading...</p>}
      {error && <div className="p-4 bg-red-100 text-red-700">{error}</div>}
      {!loading && !error && (
        <div className="overflow-x-auto">
          <Card>
            <CardHeader>
              <CardTitle>Data by Ticker</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ticker</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead>Raw</TableHead>
                    <TableHead>Cleaned</TableHead>
                    <TableHead>Features</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Array.isArray(tickers) &&
                    tickers.map((row) => (
                      <TableRow key={row.ticker}>
                        <TableCell className="font-mono">{row.ticker}</TableCell>
                        <TableCell>
                          <TickerName ticker={row.ticker} />
                        </TableCell>
                        <TableCell>
                          {row.raw
                            ? `${row.raw.start_date?.substring(0, 10) || ""}—${row.raw.end_date?.substring(0, 10) || ""} (${row.raw.row_count})`
                            : <span className="text-gray-400">None</span>}
                        </TableCell>
                        <TableCell>
                          {row.cleaned
                            ? `${row.cleaned.start_date?.substring(0, 10) || ""}—${row.cleaned.end_date?.substring(0, 10) || ""} (${row.cleaned.row_count})`
                            : <span className="text-gray-400">None</span>}
                        </TableCell>
                        <TableCell>
                          {row.features
                            ? `${row.features.start_date?.substring(0, 10) || ""}—${row.features.end_date?.substring(0, 10) || ""} (${row.features.row_count})`
                            : <span className="text-gray-400">None</span>}
                        </TableCell>
                        <TableCell>
                          {TABLE_OPTIONS.map(opt => {
                            const available = (row as any)[opt.value];
                            return (
                              <Button
                                key={opt.value}
                                variant={available ? "secondary" : "outline"}
                                disabled={!available}
                                size="sm"
                                className="mr-1 mb-1"
                                onClick={() => {
                                  if (available) {
                                    setSelectedTicker(row.ticker);
                                    setSelectedTable(opt.value as any);
                                  }
                                }}
                              >
                                View {opt.label}
                              </Button>
                            );
                          })}
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
          {selectedTicker && (
            <Card className="mt-6 bg-gray-100">
              <CardHeader>
                <CardTitle className="flex items-center gap-4 text-lg">
                  Details for {selectedTicker}: {TABLE_OPTIONS.find(opt => opt.value === selectedTable)?.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {actionStatus && <span>{actionStatus}</span>}
                {!actionStatus && tableData.length === 0 && (
                  <span>No data found for this table/ticker.</span>
                )}
                {!actionStatus && tableData.length > 0 && (
                  <pre className="overflow-x-auto text-xs bg-gray-50 rounded p-2">
                    {JSON.stringify(tableData.slice(0, 10), null, 2)}
                  </pre>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
