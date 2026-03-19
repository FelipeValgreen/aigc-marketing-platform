import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://valgreen21-aigc-backend.hf.space/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    // Si se suben archivos (FormData), Axios se encarga automáticamente de omitir el 'Content-Type' para dejar el boundary nativo del explorador.
  },
});
