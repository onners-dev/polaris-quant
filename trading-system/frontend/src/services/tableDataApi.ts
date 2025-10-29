import axios from "axios";

export async function getTableData(table: "raw" | "cleaned" | "features", ticker: string) {
  const response = await axios.get(`/api/data/table?table=${table}&ticker=${ticker}`);
  return response.data;
}
