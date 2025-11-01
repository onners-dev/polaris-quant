import axios from "axios";

export async function getDataQuality() {
  const response = await axios.get("/api/data/quality");
  return response.data;
}
