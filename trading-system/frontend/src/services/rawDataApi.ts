import axios from "axios";

export async function getRawData(ticker: string) {
  const response = await axios.get(`/api/data/raw?ticker=${ticker}`);
  return response.data;
}
