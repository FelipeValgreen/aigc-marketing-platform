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
    # Valores por defecto por si falla el scraping/LLM
    content = ""
    brand_colors = {}
    llm_result = {}
    
    # Intento de extracción inteligente
    try:
        print(f"\n🚀 Iniciando extracción ADN para: {new_client.website_url}")
        scraped_data = await scrape_website_text(new_client.website_url)
        content = scraped_data.get('content', '')
        brand_colors = scraped_data.get('brand_colors', {})
        
        print(f"🧠 Scrapeado exitoso. Iniciando análisis LLM con Gemini...")
        llm_result = await analyze_brand_voice(content, company_name=new_client.company_name, brand_colors=brand_colors)
        print("✅ Análisis IA completado.")
        
    except Exception as e:
        print(f"\n⚠️ Falló la extracción ADN inteligente: {str(e)}. Usando proceso genérico para no interrumpir el flujo.")
        # Generar guías básicas basadas en el nombre por defecto
        llm_result = {
            "tone_of_voice": "Profesional, informativo y confiable.",
            "target_audience": "Público general interesado en el rubro.",
            "value_proposition": f"Excelencia en servicios relacionados con {new_client.company_name}.",
            "primary_color_hex": "#3B82F6" # Azul moderno por defecto
        }

    # === CREAR SIEMPRE LAS BRAND GUIDELINES PARA NO BLOQUEAR EL FRONTEND ===
    new_guidelines = BrandGuidelines(
        client_id=new_client.id,
        tone_of_voice=llm_result.get('tone_of_voice', 'Profesional'),
        target_audience=llm_result.get('target_audience', 'Empresas y particulares'),
        value_proposition=llm_result.get('value_proposition', f"Servicio premium de {new_client.company_name}"),
        primary_color_hex=llm_result.get('primary_color_hex', '#3B82F6')
    )
    db.add(new_guidelines)
    db.commit()
    print(f"✅ ADN de {new_client.company_name} registrado en base de datos. (Status: OK)\n")
    
    return {
        "client": {
            "id": new_client.id,
            "company_name": new_client.company_name,
            "website_url": new_client.website_url
        },
        "guidelines": {
            "tone_of_voice": new_guidelines.tone_of_voice,
            "target_audience": new_guidelines.target_audience,
            "value_proposition": new_guidelines.value_proposition,
            "primary_color_hex": new_guidelines.primary_color_hex
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
        
    import os, json
    
    script_dict = json.loads(project.script_json)
    hook = script_dict.get('hook', {}).get('script', '')
    body = script_dict.get('body', {}).get('script', '')
    cta = script_dict.get('cta', {}).get('script', '')
    full_monologue = f"{hook} {body} {cta}".strip()
    
    avatar_id = project.avatar_id or "sofia"
    heygen_error = None
    did_error = None
    
    # === MOTOR 1: HeyGen (Premium - requiere créditos pagados) ===
    try:
        from backend.services.video_service import generate_avatar_video
        heygen_key = os.getenv("HEYGEN_API_KEY", "")
        if not heygen_key:
            raise Exception("HEYGEN_API_KEY no configurada")
        print(f"\n🎬 [MOTOR 1 - HEYGEN] Intentando para proyecto #{project.id}...")
        
        render_result = await generate_avatar_video(
            script=full_monologue,
            avatar_id=avatar_id,
            voice_id="",
            bg_video_path=project.custom_media_path
        )
        
        final_url = render_result.get("video_url")
        if final_url and final_url.startswith("/"):
            final_url = f"https://valgreen21-aigc-backend.hf.space{final_url}"
        
        project.video_url = final_url
        project.status = "COMPLETADO"
        db.commit()
        return {"project_id": project.id, "video_url": final_url, "provider": "heygen"}
        
    except Exception as e:
        heygen_error = str(e)
        print(f"\n⚠️ [HEYGEN FALLÓ] {heygen_error[:100]}")
    
    # === MOTOR 2: D-ID (Free tier - 5 min de video con avatar IA) ===
    try:
        from backend.services.did_service import generate_did_video
        did_key = os.getenv("DID_API_KEY", "")
        if not did_key:
            raise Exception("DID_API_KEY no configurada. Obtén gratis: https://studio.d-id.com")
        print(f"\n🎬 [MOTOR 2 - D-ID] Intentando avatar IA para proyecto #{project.id}...")
        
        render_result = await generate_did_video(
            script=full_monologue,
            avatar_id=avatar_id
        )
        
        final_url = render_result.get("video_url")
        if final_url and final_url.startswith("/"):
            final_url = f"https://valgreen21-aigc-backend.hf.space{final_url}"
        
        project.video_url = final_url
        project.status = "COMPLETADO"
        db.commit()
        return {"project_id": project.id, "video_url": final_url, "provider": "d-id"}
        
    except Exception as e:
        did_error = str(e)
        print(f"\n⚠️ [D-ID FALLÓ] {did_error[:100]}")
    
    # === MOTOR 3: Edge-TTS + Pexels (Siempre gratuito, busca videos UGC de personas) ===
    try:
        from backend.services.audio_service import generate_voiceover
        from backend.services.stock_video_service import download_background_video
        
        edge_voice_map = {
            "sofia":  "es-CL-CatalinaNeural",
            "mateo":  "es-MX-JorgeNeural",
            "elena":  "es-ES-ElviraNeural",
        }
        selected_voice = edge_voice_map.get(avatar_id, "es-CL-CatalinaNeural")
        
        # 1. Audio con voz regional
        base_filename = f"voiceover_proj_{project.id}_{int(time.time())}"
        audio_path, srt_path = await generate_voiceover(full_monologue, base_filename, voice=selected_voice)
        print(f"✅ Audio: {audio_path} ({selected_voice})")
        
        # 2. Video de PERSONA hablando a cámara (estilo UGC, NO del producto)
        ugc_person_queries = {
            "sofia": "woman talking to camera review product",
            "mateo": "man talking to camera review product",
            "elena": "woman presenting product to camera energetic",
        }
        person_query = ugc_person_queries.get(avatar_id, "person talking to camera")
        
        if project.custom_media_path and os.path.exists(project.custom_media_path):
            bg_video_path = project.custom_media_path
        else:
            bg_video_path = await download_background_video(person_query)
        print(f"✅ Video persona: {bg_video_path}")
        
        # Determinar URL final
        if bg_video_path and os.path.exists(bg_video_path):
            video_serve_path = f"/static/video/{os.path.basename(bg_video_path)}"
            final_url = f"https://valgreen21-aigc-backend.hf.space{video_serve_path}"
        else:
            final_url = f"https://valgreen21-aigc-backend.hf.space{audio_path}"
        
        project.video_url = final_url
        project.status = "COMPLETADO"
        db.commit()
        
        return {
            "project_id": project.id, 
            "video_url": final_url,
            "audio_url": f"https://valgreen21-aigc-backend.hf.space{audio_path}",
            "provider": "edge_tts_ugc",
            "voice": selected_voice,
            "note": "Motor Starter: Persona de stock + voz IA regional. Para avatar IA personalizado, configura D-ID_API_KEY."
        }
        
    except Exception as fallback_error:
        raise HTTPException(
            status_code=500, 
            detail=f"Los 3 motores fallaron. HeyGen: {heygen_error[:80] if heygen_error else 'N/A'} | D-ID: {did_error[:80] if did_error else 'N/A'} | Edge-TTS: {str(fallback_error)[:80]}"
        )

@router.get("/projects", status_code=status.HTTP_200_OK)
async def get_all_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()
    
@router.get("/{client_id}/projects", status_code=status.HTTP_200_OK)
async def get_client_projects(client_id: int, db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.client_id == client_id).order_by(Project.created_at.desc()).all()
