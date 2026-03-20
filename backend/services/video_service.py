import os
import asyncio
import httpx
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_GENERATE_URL = "https://api.heygen.com/v2/video/generate"
HEYGEN_STATUS_URL = "https://api.heygen.com/v1/video_status.get"

# Mapeo de Talento a IDs Reales de HeyGen
TALENT_MAPPING = {
    "sofia": {
        "avatar_id": "Daisy-casual-20220718",
        "voice_id": "es-CL-CatalinaNeural"
    },
    "mateo": {
        "avatar_id": "Eleno-in-suit-20220718",
        "voice_id": "es-MX-JorgeNeural"
    },
    "elena": {
        "avatar_id": "May-casual-20220718",
        "voice_id": "es-ES-ElviraNeural"
    }
}

async def generate_avatar_video(script: str, avatar_id: str, voice_id: str, bg_video_path: str = None) -> dict:
    """
    Orquestación Real con HeyGen API V2.
    Solicita el video, realiza polling del status y descarga el resultado final.
    """
    if not HEYGEN_API_KEY:
        raise Exception("HEYGEN_API_KEY no configurada. Verifica tu archivo .env")

    # Obtener IDs reales según la selección del usuario
    talent = TALENT_MAPPING.get(avatar_id.lower(), TALENT_MAPPING["sofia"])
    
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }

    # Estructura de Payload según HeyGen API V2
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": talent["avatar_id"],
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": talent["voice_id"]
                }
            }
        ],
        "dimension": {
            "width": 1080,
            "height": 1920
        }
    }

    print(f"\n🚀 Despachando solicitud a HeyGen V2 para Avatar: {avatar_id}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Paso A: Iniciar Generación
        response = await client.post(HEYGEN_GENERATE_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            error_detail = response.json().get("message", "Error desconocido en HeyGen")
            raise Exception(f"Fallo al iniciar video: {error_detail}")

        video_id = response.json().get("data", {}).get("video_id")
        if not video_id:
            raise Exception("No se recibió video_id de HeyGen")

        print(f"✅ Video encolado. ID: {video_id}. Iniciando Polling...")

        # Paso B: Polling (Esperar a que el video esté listo)
        status_headers = {
            "accept": "application/json",
            "X-Api-Key": HEYGEN_API_KEY
        }
        
        max_attempts = 60  # Aproximadamente 5 minutos
        attempts = 0
        final_video_url = None

        while attempts < max_attempts:
            status_res = await client.get(f"{HEYGEN_STATUS_URL}?video_id={video_id}", headers=status_headers)
            
            if status_res.status_code == 200:
                data = status_res.json().get("data", {})
                status = data.get("status")
                
                if status == "completed":
                    final_video_url = data.get("video_url")
                    print(f"\n✨ HeyGen Render Completado!")
                    break
                elif status == "failed":
                    error_msg = data.get("error", "Error interno de HeyGen")
                    raise Exception(f"El renderizado de HeyGen falló: {error_msg}")
                else:
                    print(f"⏳ Procesando AI Avatar ({status})...", end="\r")
            
            await asyncio.sleep(10)
            attempts += 1
        
        if not final_video_url:
            raise Exception("Tiempo de espera agotado para el render de HeyGen")

        # Paso C: Descargar para persistencia local
        os.makedirs("static/video", exist_ok=True)
        local_filename = f"heygen_ugc_{video_id}.mp4"
        local_path = os.path.join("static", "video", local_filename)
        
        print(f"📥 Descargando render final desde HeyGen...")
        video_data = await client.get(final_video_url)
        with open(local_path, "wb") as f:
            f.write(video_data.content)

        return {
            "status": "success",
            "video_url": f"/static/video/{local_filename}",
            "provider": "heygen_active",
            "avatar_id": avatar_id
        }
