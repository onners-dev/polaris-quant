import { useEffect, useState } from "react";
import { getAvailableData } from "../services/dataApi";
import { Link } from "react-router-dom";

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
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white shadow rounded p-6">
          <div className="text-gray-500 mb-2">Tickers Ingested</div>
          <div className="text-3xl font-bold">{tickers.length}</div>
        </div>
        <div className="bg-white shadow rounded p-6">
          <div className="text-gray-500 mb-2">Last Ingest Date</div>
          <div className="text-3xl font-bold">{lastIngest ? lastIngest.substring(0, 10) : "N/A"}</div>
        </div>
      </div>
      <div className="flex gap-4">
        <Link to="/ingest" className="bg-blue-600 text-white py-2 px-4 rounded">
          Ingest New Data
        </Link>
        <Link to="/data" className="bg-gray-200 py-2 px-4 rounded">
          Data Viewer
        </Link>
      </div>
      {/* You can add charts, recent activity/history, and more here */}
    </div>
  );
}
