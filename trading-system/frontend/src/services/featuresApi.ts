import axios from "axios";

export async function generateFeatures() {
  const response = await axios.post("/api/data/features");
  return response.data;
}
