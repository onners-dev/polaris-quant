import { useTickerMeta } from "../hooks/useTickerMeta";

export default function TickerName({ ticker }: { ticker: string }) {
  const [tickerMeta] = useTickerMeta();
  const name = tickerMeta[ticker];
  return (
    <span>
      <span className="font-mono">{ticker}</span>
      {name && <span className="text-gray-500 ml-1 text-xs">({name})</span>}
    </span>
  );
}
