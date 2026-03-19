import os
import time
import httpx
import aiofiles

async def download_background_video(query: str) -> str:
    """
    Busca y descarga un video de stock vertical desde Pexels API.
    Retorna la ruta local del archivo descargado.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    fallback_video = os.path.join("static", "video", "background.mp4")
    
    if not api_key:
        print("PEXELS_API_KEY no encontrada. Usando video de fallback.")
        return fallback_video
        
    url = "https://api.pexels.com/videos/search"
    params = {
        "query": query,
        "orientation": "portrait",
        "size": "medium",
        "per_page": 1
    }
    headers = {
        "Authorization": api_key
    }
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("videos"):
                print(f"No se encontraron videos en Pexels para '{query}'. Usando fallback.")
                return fallback_video
                
            video_data = data["videos"][0]
            # Seleccionar archivo mp4 preferiblemente HD
            video_files = video_data.get("video_files", [])
            mp4_files = [f for f in video_files if f.get("file_type") == "video/mp4"]
            
            if not mp4_files:
                return fallback_video
                
            # Elegir la primera opción disponible (Pexels suele ordenar por calidad)
            download_url = mp4_files[0]["link"]
            
            # Descargar archivo
            bg_filename = f"bg_{int(time.time())}.mp4"
            os.makedirs("static/video", exist_ok=True)
            bg_filepath = os.path.join("static", "video", bg_filename)
            
            print(f"Descargando video de stock desde Pexels: {download_url}")
            async with client.stream("GET", download_url) as dl_resp:
                dl_resp.raise_for_status()
                async with aiofiles.open(bg_filepath, "wb") as f:
                    async for chunk in dl_resp.aiter_bytes():
                        await f.write(chunk)
                        
            return bg_filepath
            
    except Exception as e:
        print(f"Error bajando video de Pexels: {str(e)}. Usando fallback.")
        return fallback_video
