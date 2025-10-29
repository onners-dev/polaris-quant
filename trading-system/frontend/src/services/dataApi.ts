import axios from "axios";

export async function getAvailableData() {

  const response = await axios.get("/api/data/available");

  return response.data;

}

