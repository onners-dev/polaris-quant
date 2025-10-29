import axios from "axios";

export async function trainModel(tickers: string[], target = "Return_1d") {
  const response = await axios.post("/api/models/train", { tickers, target });
  return response.data;
}
