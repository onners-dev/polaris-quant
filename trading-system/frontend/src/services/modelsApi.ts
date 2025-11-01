import axios from "axios";

export async function listModels({ ticker }: { ticker?: string } = {}) {
  let url = `/api/models/list`;
  if (ticker) url += `?ticker=${encodeURIComponent(ticker)}`;
  const response = await axios.get(url);
  return response.data;
}

export async function getModelDetails(model_id: string) {
  const response = await axios.get(`/api/models/${model_id}`);
  return response.data;
}
