import axios from "axios";

export async function ingestYahooStock(tickers: string[], start: string, end: string, interval: string = '1d') {
  const response = await axios.post("/api/ingest", {
    tickers,
    start,
    end,
    interval
  });
  return response.data;
}
