import axios from "axios";

export async function getLatestDataHash() {
  const response = await axios.get("/api/data/latest-hash");
  return response.data;
}
