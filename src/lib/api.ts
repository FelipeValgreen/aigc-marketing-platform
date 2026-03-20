import axios from 'axios';

// Detectamos si estamos en producción (Vercel) para usar la URL de Hugging Face
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {},
});
