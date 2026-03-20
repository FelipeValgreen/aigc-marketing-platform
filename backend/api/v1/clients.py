from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.models.models import Client, BrandGuidelines, Project
from backend.schemas.schemas import ClientCreate, ClientOut, ProjectCreate
from backend.services.scraper_service import scrape_website_text
from backend.services.llm_service import analyze_brand_voice, generate_video_script, generate_carousel_and_copy
from backend.schemas.schemas import ScriptRequest, GenerateAudioRequest
import asyncio
import time

router = APIRouter()

@router.post("/onboarding", status_code=status.HTTP_201_CREATED)
async def onboarding_client(client_in: ClientCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo cliente proporcionando el nombre de la empresa y la URL del sitio web.
    """
    # Verificamos si ya existe la URL ingresada
    existing_client = db.query(Client).filter(Client.website_url == str(client_in.website_url)).first()
    if existing_client:
        print(f"🔄 Cliente existente detectado ({existing_client.company_name}). Recuperando información...")
        guidelines = db.query(BrandGuidelines).filter(BrandGuidelines.client_id == existing_client.id).first()
        return {
            "client": {
                "id": existing_client.id,
                "company_name": existing_client.company_name,
                "website_url": existing_client.website_url
            },
            "guidelines": {
                "tone_of_voice": guidelines.tone_of_voice if guidelines else None,
                "target_audience": guidelines.target_audience if guidelines else None,
                "value_proposition": guidelines.value_proposition if guidelines else None,
                "primary_color_hex": guidelines.primary_color_hex if guidelines else None
            }
        }
    
    # Crear el nuevo registro de cliente (se guarda como string)
    new_client = Client(
        company_name=client_in.company_name,
        website_url=str(client_in.website_url)
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    # Invocar el scraper y LLM de forma asíncrona
    try:
        print(f"\n🚀 Iniciando scraping para la URL: {new_client.website_url}")
        scraped_data = await scrape_website_text(new_client.website_url)
        content = scraped_data['content']
        brand_colors = scraped_data.get('brand_colors', {})
        
        print(f"🧠 Escrapeado exitoso. Colores detectados: {brand_colors.get('detected_colors', [])[:5]}")
        print(f"🎨 Color más frecuente: {brand_colors.get('most_frequent', 'N/A')}")
        print(f"🧠 Iniciando análisis LLM con Gemini...")
        llm_result = await analyze_brand_voice(content, brand_colors=brand_colors)
        
        # Crear y guardar en BrandGuidelines asociado al cliente
        new_guidelines = BrandGuidelines(
            client_id=new_client.id,
            tone_of_voice=llm_result.get('tone_of_voice', ''),
            target_audience=llm_result.get('target_audience', ''),
            value_proposition=llm_result.get('value_proposition', ''),
            primary_color_hex=llm_result.get('primary_color_hex', '#FFFF00')
        )
        db.add(new_guidelines)
        db.commit()
        
        print("--- RESULTADO DEL LLM GUARDADO EN DB ---")
        print(f"Tono de Voz: {new_guidelines.tone_of_voice}")
        print(f"Público Objetivo: {llm_result.get('target_audience')}")
        print(f"Propuesta de Valor: {llm_result.get('value_proposition')}")
        print("----------------------------------------\n")
        
    except Exception as e:
        print(f"\n❌ Error en el proceso (Scraper/LLM) para {new_client.website_url}: {str(e)}\n")
    
    return {
        "client": {
            "id": new_client.id,
            "company_name": new_client.company_name,
            "website_url": new_client.website_url
        },
        "guidelines": {
            "tone_of_voice": new_guidelines.tone_of_voice if 'new_guidelines' in locals() else None,
            "target_audience": new_guidelines.target_audience if 'new_guidelines' in locals() else None,
            "value_proposition": new_guidelines.value_proposition if 'new_guidelines' in locals() else None,
            "primary_color_hex": new_guidelines.primary_color_hex if 'new_guidelines' in locals() else None
        }
    }

@router.post("/{client_id}/generate-script", status_code=status.HTTP_200_OK)
async def generate_script_endpoint(client_id: int, script_req: ScriptRequest, db: Session = Depends(get_db)):
    guidelines = db.query(BrandGuidelines).filter(BrandGuidelines.client_id == client_id).first()
    if not guidelines:
        raise HTTPException(status_code=404, detail="Brand Guidelines no encontradas para este cliente")
    
    brand_context = {
        "tone_of_voice": guidelines.tone_of_voice,
        "target_audience": guidelines.target_audience,
        "value_proposition": guidelines.value_proposition
    }
    
    product_info = f"{script_req.product_name}: {script_req.product_description}"
    
    try:
        script_json = await generate_video_script(brand_context, product_info)
        return script_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{client_id}/generate-social-pack", status_code=status.HTTP_200_OK)
async def generate_social_pack_endpoint(client_id: int, script_req: ScriptRequest, db: Session = Depends(get_db)):
    guidelines = db.query(BrandGuidelines).filter(BrandGuidelines.client_id == client_id).first()
    if not guidelines:
        raise HTTPException(status_code=404, detail="Brand Guidelines no encontradas para este cliente")
    
    brand_context = {
        "tone_of_voice": guidelines.tone_of_voice,
        "target_audience": guidelines.target_audience,
        "value_proposition": guidelines.value_proposition
    }
    
    product_info = f"{script_req.product_name}: {script_req.product_description}"
    
    try:
        social_pack = await generate_carousel_and_copy(brand_context, product_info)
        return social_pack
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    client_id: int = Form(...),
    product_name: str = Form(...),
    product_desc: str = Form(...),
    video_angle: str = Form("UGC Tradicional"),
    music_style: str = Form("Sin Música"),
    avatar_id: str = Form("sofia"),
    custom_media: UploadFile = File(None),
    db: Session = Depends(get_db)):
    
    guidelines = db.query(BrandGuidelines).filter(BrandGuidelines.client_id == client_id).first()
    if not guidelines:
        raise HTTPException(status_code=404, detail="Brand Guidelines no encontradas")
        
    custom_media_path = None
    import os, shutil
    if custom_media and custom_media.filename:
        os.makedirs("static/uploads", exist_ok=True)
        ext = custom_media.filename.split('.')[-1]
        unique_filename = f"proj_media_{client_id}_{int(time.time())}.{ext}"
        filepath = os.path.join("static", "uploads", unique_filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(custom_media.file, buffer)
        custom_media_path = filepath
        
    new_project = Project(
        client_id=client_id,
        product_name=product_name,
        product_desc=product_desc,
        video_angle=video_angle,
        music_style=music_style,
        avatar_id=avatar_id,
        custom_media_path=custom_media_path,
        status="ESPERANDO_GUION"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    brand_context = {
        "tone_of_voice": guidelines.tone_of_voice,
        "target_audience": guidelines.target_audience,
        "value_proposition": guidelines.value_proposition
    }
    product_info = f"{product_name}: {product_desc}"
    import json
    try:
        script_json = await generate_video_script(brand_context, product_info, angle=video_angle)
        new_project.script_json = json.dumps(script_json)
        new_project.status = "GUION_LISTO"
        db.commit()
        db.refresh(new_project)
        return {"project_id": new_project.id, "status": new_project.status, "script": script_json, "video_angle": video_angle}
    except Exception as e:
        db.delete(new_project)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/approve-and-render", status_code=status.HTTP_200_OK)
async def approve_and_render_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    client_id = project.client_id
    base_filename = f"voiceover_proj_{project.id}_{int(time.time())}"
    video_filename = f"ugc_proj_{project.id}_{int(time.time())}.mp4"
    audio_url = None
    vtt_url = None
    bg_video_path = None
    import os, json
    
    try:
        from backend.services.video_service import generate_avatar_video
        
        script_dict = json.loads(project.script_json)
        # Extraemos el guion completo como un monólogo hablando a cámara
        hook = script_dict.get('hook', {}).get('script', '')
        body = script_dict.get('body', {}).get('script', '')
        cta = script_dict.get('cta', {}).get('script', '')
        full_monologue = f"{hook} {body} {cta}".strip()
        
        # Mapeo de Voces (Mock) para que coincida con el Avatar
        voice_map = {"sofia": "es-CL-CatalinaNeural", "mateo": "es-MX-JorgeNeural", "elena": "es-ES-ElviraNeural"}
        selected_voice = voice_map.get(project.avatar_id, "es-CL-CatalinaNeural")

        # Orquestación con el nuevo servicio de AVATARES (Paso al futuro HeyGen)
        render_result = await generate_avatar_video(
            script=full_monologue,
            avatar_id=project.avatar_id or "sofia",
            voice_id=selected_voice,
            bg_video_path=project.custom_media_path
        )
        
        final_url = f"http://localhost:8000{render_result.get('video_url')}"
        project.video_url = final_url
        project.status = "COMPLETADO"
        db.commit()
        
        return {"project_id": project.id, "video_url": final_url, "provider": render_result.get("provider")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en Orquestador de Avatares: {str(e)}")
    finally:
        def remove_if_exists(filepath):
            if filepath and os.path.exists(filepath):
                try: os.remove(filepath)
                except: pass
        if audio_url: remove_if_exists(audio_url.lstrip('/'))
        if vtt_url: remove_if_exists(vtt_url.lstrip('/'))
        if bg_video_path and os.path.basename(bg_video_path).startswith("bg_"):
            remove_if_exists(bg_video_path.lstrip('/'))

@router.get("/projects", status_code=status.HTTP_200_OK)
async def get_all_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()
    
@router.get("/{client_id}/projects", status_code=status.HTTP_200_OK)
async def get_client_projects(client_id: int, db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.client_id == client_id).order_by(Project.created_at.desc()).all()
