import os
import asyncio
from backend.services.stock_video_service import download_background_video

def hex_to_ass_color(hex_color: str) -> str:
    """Convierte #RRGGBB a formato ASS de FFmpeg &HBBGGRR&"""
    if not hex_color:
        return "&H00FFFF&"
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H{b}{g}{r}&"
    return "&H00FFFF&"

async def assemble_ugc_video(audio_path: str, vtt_path: str, output_filename: str, bg_video_path: str = None, music_style: str = "Sin Música", primary_color_hex: str = "#FFFF00") -> str:
    """
    Ensambla el video final usando FFmpeg.
    """
    os.makedirs("static/video", exist_ok=True)
    
    # Remove leading slashes to get relative paths
    audio_file = audio_path.lstrip('/')
    vtt_file = vtt_path.lstrip('/')
    
    valid_exts = ('.mp4', '.mov', '.avi', '.jpg', '.jpeg', '.png')
    if not bg_video_path or not bg_video_path.lower().endswith(valid_exts):
        print("Ignorando archivo no compatible (ej. PDF). Retornando a Pexels AI...")
        bg_video_path = await download_background_video(output_filename.split('_')[1] if output_filename else "abstract")
        
    bg_video = bg_video_path.lstrip('/')
    output_filepath = os.path.join("static", "video", output_filename)
    
    if not os.path.exists(bg_video):
        raise FileNotFoundError(f"El video de fondo {bg_video} no existe. Por favor descárgalo.")
        
    ass_color = hex_to_ass_color(primary_color_hex)
    vtt_filter_path = vtt_file.replace('\\', '/')
    sub_filter = f"subtitles={vtt_filter_path}:force_style='Fontname=Arial,FontSize=24,PrimaryColour={ass_color},Outline=1,Shadow=1,Alignment=2,MarginV=20'"
    
    music_map = {
        "Upbeat (Dinámico)": "upbeat.mp3",
        "Corporativo (Serio)": "corporativo.mp3",
        "Lo-Fi (Relajado)": "lofi.mp3"
    }
    music_path = None
    if music_style and music_style in music_map:
        m_path = os.path.join("static", "music", music_map[music_style])
        if os.path.exists(m_path):
            music_path = m_path
    
    cmd = ["ffmpeg", "-y"]
    
    if bg_video.lower().endswith(('.jpg', '.jpeg', '.png')):
        cmd.extend(["-loop", "1", "-i", bg_video])
        vf_chain = f"scale=-1:1920,crop=1080:1920,{sub_filter}"
        is_image = True
    else:
        cmd.extend(["-stream_loop", "-1", "-i", bg_video])
        vf_chain = f"crop=ih*(9/16):ih,{sub_filter}"
        is_image = False
        
    cmd.extend(["-i", audio_file])
    
    if music_path:
        cmd.extend(["-stream_loop", "-1", "-i", music_path])
        audio_filter = "[1:a]volume=1.0[a1];[2:a]volume=0.15[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
        cmd.extend(["-filter_complex", f"[0:v]{vf_chain}[v_out];{audio_filter}"])
        cmd.extend(["-map", "[v_out]", "-map", "[a_out]"])
    else:
        cmd.extend(["-vf", vf_chain])
        
    cmd.extend(["-shortest", "-c:v", "libx264"])
    
    if is_image:
        cmd.extend(["-tune", "stillimage"])
        
    cmd.extend(["-c:a", "aac"])
    if is_image:
        cmd.extend(["-pix_fmt", "yuv420p"])
        
    cmd.extend([output_filepath])
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"FFmpeg falló: {stderr.decode()}")
        
    return f"/static/video/{output_filename}"
