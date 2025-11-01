import { useEffect, useState } from "react";
import { getDataQuality } from "../services/dataQualityApi";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type Quality = {
  percent_missing: number;
  last_valid_date: string | null;
  outlier_count: number;
};

export default function DataQuality() {
  const [data, setData] = useState<{ [ticker: string]: { [feat: string]: Quality } }>({});
  const [lastDate, setLastDate] = useState<string>("");
  const [alerts, setAlerts] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDataQuality().then(res => {
      setData(res.data);
      setLastDate(res.last_date);
      setAlerts(res.alerts || []);
      setLoading(false);
    });
  }, []);

  const allRows = Object.entries(data).flatMap(([ticker, feats]) =>
    Object.entries(feats).map(([feat, vals]) => ({
      ticker, feature: feat, ...vals
    }))
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8 p-8">
      <Card>
        <CardHeader>
          <CardTitle>Data Quality & Monitoring</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 text-sm text-gray-700">
            <strong>Latest data date:</strong> {lastDate}
          </div>
          {alerts.length > 0 && (
            <div className="p-2 bg-yellow-200 text-yellow-900 rounded mb-4">
              <ul className="list-disc ml-5">{alerts.map(a => <li key={a}>{a}</li>)}</ul>
            </div>
          )}
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ticker</TableHead>
                    <TableHead>Feature</TableHead>
                    <TableHead>% Missing</TableHead>
                    <TableHead>Last Valid Date</TableHead>
                    <TableHead>Outliers (&gt;5σ)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {allRows.map(row => (
                    <TableRow key={`${row.ticker}_${row.feature}`}>
                      <TableCell>{row.ticker}</TableCell>
                      <TableCell>{row.feature}</TableCell>
                      <TableCell className={row.percent_missing > 10 ? "text-red-600 font-semibold" : ""}>{row.percent_missing.toFixed(2)}%</TableCell>
                      <TableCell>{row.last_valid_date}</TableCell>
                      <TableCell className={row.outlier_count > 10 ? "text-red-600 font-semibold" : ""}>{row.outlier_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
