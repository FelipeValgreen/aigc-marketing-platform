import os
import edge_tts
import aiofiles

async def generate_voiceover(text: str, filename: str, voice: str = "es-CL-CatalinaNeural") -> tuple[str, str]:
    """
    Genera un archivo de audio a partir de texto utilizando edge-tts.
    Guarda el archivo y sus subtítulos en static/audio.
    Retorna la tupla (audio_url, vtt_url).
    """
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    
    # Asegurar que el directorio exista por si acaso
    os.makedirs("static/audio", exist_ok=True)
    
    mp3_filepath = os.path.join("static", "audio", f"{filename}.mp3")
    vtt_filepath = os.path.join("static", "audio", f"{filename}.srt")
    
    async with aiofiles.open(mp3_filepath, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                await audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    async with aiofiles.open(vtt_filepath, "w", encoding="utf-8") as vtt_file:
        await vtt_file.write(submaker.get_srt())
    
    return f"/static/audio/{filename}.mp3", f"/static/audio/{filename}.srt"
