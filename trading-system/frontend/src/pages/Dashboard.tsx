import { useEffect, useState } from "react";
import { getAvailableData } from "../services/dataApi";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const [tickers, setTickers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getAvailableData()
      .then((data) => setTickers(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false));
  }, []);

  const lastIngest = tickers.reduce(
    (latest, t) => (latest && t.end_date > latest ? t.end_date : t.end_date),
    tickers[0]?.end_date
  );

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold mb-8">Dashboard</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-gray-500 text-base font-normal">Tickers Ingested</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{tickers.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-gray-500 text-base font-normal">Last Ingest Date</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{lastIngest ? lastIngest.substring(0, 10) : "N/A"}</div>
          </CardContent>
        </Card>
      </div>
      <div className="flex flex-col sm:flex-row gap-4">
        <Link to="/ingest" className="w-full sm:w-auto">
          <Button className="w-full" size="lg">Ingest New Data</Button>
        </Link>
        <Link to="/data" className="w-full sm:w-auto">
          <Button variant="secondary" className="w-full" size="lg">
            Data Viewer
          </Button>
        </Link>
      </div>
      {/* You can add charts, recent activity/history, and more here */}
    </div>
  );
}
