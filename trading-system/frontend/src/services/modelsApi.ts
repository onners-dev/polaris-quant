import axios from "axios";

export async function listModels(ticker?: string) {
  const url = ticker ? `/api/models/list?ticker=${ticker}` : `/api/models/list`;
  const response = await axios.get(url);
  return response.data;
}

export async function getModelDetails(model_id: string) {
  const response = await axios.get(`/api/models/${model_id}`);
  return response.data;
}
