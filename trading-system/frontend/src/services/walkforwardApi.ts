import axios from "axios";

export interface WalkForwardParams {
  model_id: string;
  tickers?: string[];
  full_start: string;
  full_end: string;
  window_train: number;
  window_test: number;
  stride?: number;
  transaction_cost_bps?: number;
  slippage_bps?: number;
}

export async function runWalkForward(params: WalkForwardParams) {
  const response = await axios.post("/api/backtest/walkforward", params);
  return response.data;
}
