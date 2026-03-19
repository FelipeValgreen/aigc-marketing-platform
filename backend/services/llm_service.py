import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configurar el cliente de Gemini usando la API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "tu_api_key_aqui":
    genai.configure(api_key=api_key)

async def analyze_brand_voice(website_text: str) -> dict:
    """
    Analiza el texto de una web y extrae el perfil de marca usando Gemini 1.5 Flash.
    """
    if not api_key or api_key == "tu_api_key_aqui":
        raise Exception("API Key de Gemini no configurada correctamente en el archivo .env")

    # Limitar a 3000 caracteres para no saturar el token limit
    text_to_analyze = website_text[:3000]
    
    prompt = f"""Eres un estratega de marketing. Analiza el siguiente texto extraído de una página web y define el perfil de la marca. 
Devuelve ÚNICAMENTE un objeto JSON puro (SIN texto adicional, SIN usar bloques de código Markdown) con las siguientes claves: 
'tone_of_voice' (ej. formal, industrial, cercano), 
'target_audience' (descripción breve del cliente ideal), 
'value_proposition' (qué problema resuelven) y
'primary_color_hex' (Intenta adivinar el color principal de la marca en base al sector si no es obvio, en formato HEX, ej: #FF0000. Si dudas, usa #FFFF00).

Texto de la web:
{text_to_analyze}
"""
    
    # Instanciar el modelo
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = await model.generate_content_async(prompt)
        result_text = response.text.strip()
        
        # Limpiar el formato por si el LLM devuelve el JSON dentro de bloques de código markdown
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text.strip())
        
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON del LLM. Respuesta fue: {result_text}")
        return {
            "tone_of_voice": "Neutro / Corporativo (Fallback Automático)",
            "target_audience": "Público objetivo general (Fallback Automático)",
            "value_proposition": "Servicios o productos de calidad (Fallback Automático)",
            "primary_color_hex": "#FFFF00"
        }
    except Exception as e:
        print(f"Error comunicándose con Gemini: {str(e)}")
        return {
            "tone_of_voice": "Neutro / Corporativo (Fallback Automático)",
            "target_audience": "Público objetivo general (Fallback Automático)",
            "value_proposition": "Servicios o productos de calidad (Fallback Automático)",
            "primary_color_hex": "#FFFF00"
        }

async def generate_video_script(brand_context: dict, product_info: str, angle: str = "UGC Tradicional") -> dict:
    if not api_key or api_key == "tu_api_key_aqui":
        raise Exception("API Key de Gemini no configurada correctamente en el archivo .env")
        
    prompt = f"""Eres un creador de contenido UGC experto en TikTok y Reels. Escribe un guion de 30 segundos para un video promocional del siguiente producto: {product_info}. DEBES adoptar estrictamente el siguiente tono de voz: {brand_context.get('tone_of_voice', 'normal')} y dirigirte a este público: {brand_context.get('target_audience', 'general')}. La estructura y enfoque psicológico del guion debe ser ESTRICTAMENTE un formato de: [{angle}]. Adapta el gancho, el cuerpo y el CTA a este formato específico. La propuesta de valor central de la empresa es: {brand_context.get('value_proposition', '')}. 
Devuelve ÚNICAMENTE un JSON puro con tres claves principales: 'hook', 'body' y 'cta'. 
Cada una de esas claves DEBE ser un objeto JSON que contenga exactamente dos claves internas: 'script' (el texto exacto que el actor debe decir) y 'visuals' (instrucciones breves de dirección de cámara o texto en pantalla)."""

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = await model.generate_content_async(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text.strip())
        
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON del LLM al crear guion. Respuesta fue: {result_text}")
        raise e
    except Exception as e:
        print(f"Error comunicándose con Gemini para guion: {str(e)}")
        raise e

async def generate_carousel_and_copy(brand_context: dict, product_info: str) -> dict:
    if not api_key or api_key == "tu_api_key_aqui":
        raise Exception("API Key de Gemini no configurada correctamente en el archivo .env")

    prompt = f"""Eres un Copywriter experto. Crea un paquete de contenido para Instagram/LinkedIn sobre este producto: [{product_info}]. Usa ESTRICTAMENTE este tono de voz: [{brand_context.get('tone_of_voice')}] y dirígete a: [{brand_context.get('target_audience')}]. Propuesta de valor: [{brand_context.get('value_proposition')}]. Devuelve ÚNICAMENTE un JSON puro (sin Markdown ni texto adicional) con esta estructura: 'caption' (el texto principal del post con emojis), 'hashtags' (lista de 5 a 8 hashtags strings), y 'carousel_slides' (una lista de objetos, donde cada objeto represente una diapositiva del carrusel, con un máximo de 5 diapositivas. Cada diapositiva debe tener 'slide_number', 'text' y 'visual_concept' [qué debería mostrar el diseño gráfico])."""

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = await model.generate_content_async(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text.strip())
        
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON del LLM al crear carrusel. Respuesta fue: {result_text}")
        return {
            "caption": "¡Hola! Tuvimos un pequeño inconveniente procesando el formato con la IA, pero estamos mejorando a cada minuto. ¡Mira nuestro slide de prueba!",
            "hashtags": ["#marketing", "#error", "#aigc"],
            "carousel_slides": [{"slide_number": 1, "text": f"Descubre {product_info}", "visual_concept": "Fondo minimalista con el nombre de la marca"}]
        }
    except Exception as e:
        print(f"Error comunicándose con Gemini para carrusel: {str(e)}")
        return {
            "caption": "Generación temporalmente suspendida.",
            "hashtags": ["#mantenimiento"],
            "carousel_slides": [{"slide_number": 1, "text": "Mantenimiento activo", "visual_concept": "Icono genérico"}]
        }
