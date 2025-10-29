import axios from "axios";

export async function getFeaturesData(ticker: string) {
  const response = await axios.get(`/api/data/features?ticker=${ticker}`);
  return response.data;
}
