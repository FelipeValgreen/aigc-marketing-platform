import axios from 'axios';

// Detectamos si estamos en producción (Vercel) para usar la URL de Hugging Face
const API_BASE_URL = "https://valgreen21-aigc-backend.hf.space/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {},
});
