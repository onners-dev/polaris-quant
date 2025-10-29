import { useEffect, useState } from "react";

// Loads /tickers.json and returns a symbol->name map, and a look up function.
export function useTickerMeta(): [{ [symbol: string]: string }, boolean] {
  const [meta, setMeta] = useState<{ [symbol: string]: string }>({});
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    fetch("/tickers.json")
      .then(res => res.json())
      .then((data: { symbol: string; name: string }[]) => {
        const map = Object.fromEntries(data.map(row => [row.symbol, row.name]));
        setMeta(map);
        setLoaded(true);
      })
      .catch(() => {
        setMeta({});
        setLoaded(true);
      });
  }, []);
  return [meta, loaded];
}
