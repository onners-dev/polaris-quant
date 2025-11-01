import axios from "axios";

export interface BacktestParams {
  model_id: string;
  tickers?: string[];
  start_date?: string;
  end_date?: string;
  transaction_cost_bps?: number;
  slippage_bps?: number;
}

export async function runBacktest(params: BacktestParams) {
  const response = await axios.post("/api/backtest/run", params);
  return response.data;
}

export async function getBacktestResult(run_id: string) {
  const response = await axios.get(`/api/backtest/${run_id}`);
  return response.data;
}

export async function listBacktests(model_id?: string, limit: number = 20) {
  const url = model_id
    ? `/api/backtest/list?model_id=${encodeURIComponent(model_id)}&limit=${limit}`
    : `/api/backtest/list?limit=${limit}`;
  const response = await axios.get(url);
  return response.data;
}
