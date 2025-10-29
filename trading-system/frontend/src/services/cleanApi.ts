import axios from "axios";

export async function cleanData() {
  const response = await axios.post("/api/data/clean");
  return response.data;
}
