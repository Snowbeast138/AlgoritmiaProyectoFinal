// client/src/services/api.ts
import axios from "axios";

const API_URL = "http://localhost:5000"; // Asegúrate de que el backend esté corriendo aquí

export const getAttractions = async () => {
  const response = await axios.get(`${API_URL}/api/attractions`);
  return response.data;
};

export const getRecommendations = async (preferences: {
  interests: string[];
  duration: number;
  budget: string;
}) => {
  const response = await axios.post(
    `${API_URL}/api/recommendations`,
    preferences
  );
  return response.data;
};
