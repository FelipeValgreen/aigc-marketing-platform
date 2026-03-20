import os
import time
import httpx
import aiofiles

DID_API_URL = "https://api.d-id.com/talks"
DID_API_KEY = os.getenv("DID_API_KEY", "")

# URLs públicas de las fotos de avatar IA (servidas desde el backend)
AVATAR_PHOTOS = {
    "sofia": "https://valgreen21-aigc-backend.hf.space/static/avatars/sofia.png",
    "mateo": "https://valgreen21-aigc-backend.hf.space/static/avatars/mateo.png",
    "elena": "https://valgreen21-aigc-backend.hf.space/static/avatars/elena.png",
}

# Voces de D-ID - usan Microsoft Azure TTS internamente
DID_VOICE_MAP = {
    "sofia": {"type": "microsoft", "voice_id": "es-CL-CatalinaNeural"},
    "mateo": {"type": "microsoft", "voice_id": "es-MX-JorgeNeural"},
    "elena": {"type": "microsoft", "voice_id": "es-ES-ElviraNeural"},
}


async def generate_did_video(script: str, avatar_id: str = "sofia") -> dict:
    """
    Genera un video con D-ID: toma la foto del avatar IA + texto y produce
    un video de la persona hablando con lip-sync.
    
    D-ID Free Tier: ~5 minutos de video, sin tarjeta de crédito.
    """
    if not DID_API_KEY:
        raise Exception("DID_API_KEY no configurada. Obtén tu key gratis en https://studio.d-id.com")
    
    photo_url = AVATAR_PHOTOS.get(avatar_id, AVATAR_PHOTOS["sofia"])
    voice_config = DID_VOICE_MAP.get(avatar_id, DID_VOICE_MAP["sofia"])
    
    headers = {
        "Authorization": f"Basic {DID_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    payload = {
        "source_url": photo_url,
        "script": {
            "type": "text",
            "input": script,
            "provider": voice_config,
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.5,
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Crear el talk
        print(f"🎬 [D-ID] Creando video con avatar {avatar_id}...")
        response = await client.post(DID_API_URL, json=payload, headers=headers)
        
        if response.status_code != 201:
            error_detail = response.text
            raise Exception(f"D-ID API error ({response.status_code}): {error_detail}")
        
        talk_data = response.json()
        talk_id = talk_data.get("id")
        print(f"✅ [D-ID] Talk creado: {talk_id}")
        
        # 2. Polling hasta completar (máx 2 min)
        status_url = f"{DID_API_URL}/{talk_id}"
        max_attempts = 24  # 24 * 5s = 2 minutos
        
        for attempt in range(max_attempts):
            import asyncio
            await asyncio.sleep(5)
            
            status_response = await client.get(status_url, headers=headers)
            status_data = status_response.json()
            current_status = status_data.get("status", "")
            
            print(f"⏳ [D-ID] Intento {attempt+1}: status={current_status}")
            
            if current_status == "done":
                result_url = status_data.get("result_url")
                if not result_url:
                    raise Exception("D-ID completó pero no devolvió URL del video")
                
                # 3. Descargar video localmente
                os.makedirs("static/video", exist_ok=True)
                local_filename = f"did_{avatar_id}_{int(time.time())}.mp4"
                local_path = os.path.join("static", "video", local_filename)
                
                print(f"📥 [D-ID] Descargando video desde: {result_url}")
                dl_response = await client.get(result_url)
                dl_response.raise_for_status()
                
                async with aiofiles.open(local_path, "wb") as f:
                    await f.write(dl_response.content)
                
                print(f"✅ [D-ID] Video guardado: {local_path}")
                return {
                    "video_url": f"/static/video/{local_filename}",
                    "provider": "d-id",
                    "avatar": avatar_id,
                }
            
            elif current_status == "error":
                error_msg = status_data.get("error", {}).get("description", "Error desconocido")
                raise Exception(f"D-ID renderizado falló: {error_msg}")
        
        raise Exception("D-ID timeout: video no completó en 2 minutos")
