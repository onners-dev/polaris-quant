import { useEffect, useState } from "react";

type TickerRecord = { symbol: string; name: string };

type Props = {
  value: string;
  onChange: (ticker: string) => void;
};

export default function TickerAutocomplete({ value, onChange }: Props) {
  const [input, setInput] = useState(value ?? "");
  const [options, setOptions] = useState<TickerRecord[]>([]);
  const [show, setShow] = useState(false);

  useEffect(() => {
    fetch("/tickers.json")
      .then((res) => res.json())
      .then(setOptions)
      .catch(() => setOptions([]));
  }, []);

  const filtered = options.filter(
    (opt) =>
      opt.symbol.toLowerCase().includes(input.toLowerCase()) ||
      opt.name.toLowerCase().includes(input.toLowerCase())
  ).slice(0, 10);

  return (
    <div className="relative">
      <input
        className="border rounded px-3 py-2 w-full"
        value={input}
        onFocus={() => setShow(true)}
        onChange={e => {
          setInput(e.target.value);
          setShow(true);
          onChange(e.target.value);
        }}
        placeholder="Start typing company or ticker"
        autoComplete="off"
      />
      {show && filtered.length > 0 && (
        <div className="absolute z-10 w-full bg-white border border-gray-200 rounded max-h-64 overflow-auto">
          {filtered.map(opt => (
            <div
              key={opt.symbol}
              className="px-3 py-2 hover:bg-blue-100 cursor-pointer"
              onMouseDown={() => {
                setInput(opt.symbol);
                setShow(false);
                onChange(opt.symbol);
              }}
            >
              <span className="font-semibold">{opt.symbol}</span>
              <span className="text-gray-500 ml-2 text-sm">{opt.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
