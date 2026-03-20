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

async def analyze_brand_voice(website_text: str, brand_colors: dict = None) -> dict:
    """
    Analiza el texto de una web y extrae el perfil de marca usando Gemini.
    Ahora recibe colores reales extraídos del CSS/HTML del sitio.
    """
    if not api_key or api_key == "tu_api_key_aqui":
        raise Exception("API Key de Gemini no configurada correctamente en el archivo .env")

    text_to_analyze = website_text[:3000]
    
    # Construir contexto de colores para el LLM
    color_context = ""
    if brand_colors:
        detected = brand_colors.get("detected_colors", [])
        sources = brand_colors.get("color_sources", {})
        most_freq = brand_colors.get("most_frequent")
        logo_urls = brand_colors.get("logo_urls", [])
        
        color_context = f"""

DATOS DE COLORES EXTRAÍDOS DEL SITIO WEB (REALES, NO INVENTADOS):
- Colores detectados en CSS/HTML (ordenados por frecuencia): {', '.join(detected[:8]) if detected else 'No se detectaron colores'}
- Color más frecuente en el sitio: {most_freq or 'No detectado'}
- Fuentes de cada color: {json.dumps(sources, ensure_ascii=False) if sources else 'N/A'}
- URLs de logo/favicon encontradas: {', '.join(logo_urls) if logo_urls else 'No encontradas'}

INSTRUCCIÓN CRÍTICA PARA EL COLOR:
- El color primario DEBE ser el color real del logo o la identidad visual de la marca.
- Prioriza: (1) meta theme-color, (2) CSS variables con nombre 'primary/brand/accent', (3) color de botones principales, (4) color más frecuente no-neutro.
- NUNCA adivines un color genérico del sector. USA los datos reales de arriba.
- Si los datos muestran un color claro como primario pero hay uno más saturado/vibrante como secundario, elige el más vibrante como primario de marca.
"""

    prompt = f"""Eres un estratega de marketing y diseñador de identidad corporativa senior. Analiza el siguiente texto extraído de una página web y define el perfil EXACTO de la marca.
{color_context}
Devuelve ÚNICAMENTE un objeto JSON puro (SIN texto adicional, SIN bloques de código Markdown) con estas claves: 
'tone_of_voice' (ej. formal, industrial, cercano - sé específico y detallado),
'target_audience' (descripción precisa del cliente ideal, incluyendo ubicación geográfica si la detectas),
'value_proposition' (qué problema específico resuelven y cómo) y
'primary_color_hex' (el color REAL de la marca en formato HEX basado en los datos de colores extraídos arriba. NO adivines. Si no hay datos de color, analiza el nombre de la empresa y su sector para una estimación educada).

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
        
    prompt = f"""Eres un Director de Guiones para Avatares de IA hiperrealistas (estilo HeyGen/Synthesia). 
Escribe un monólogo persuasivo de 30 segundos para un video promocional del siguiente producto: {product_info}. 
EL AVATAR HABLARÁ DIRECTO A LA CÁMARA.

DEBES:
1. Adoptar estrictamente este tono de voz: {brand_context.get('tone_of_voice', 'normal')}.
2. Dirigirte a este público: {brand_context.get('target_audience', 'general')}.
3. Seguir el enfoque psicológico de: [{angle}].
4. La propuesta de valor central es: {brand_context.get('value_proposition', '')}.

Devuelve ÚNICAMENTE un JSON puro con tres claves: 'hook', 'body' y 'cta'.
Cada clave DEBE ser un objeto con:
- 'script': El texto exacto que el AVATAR dirá (natural, conversacional, con pausas).
- 'visuals': Instrucciones breves de lenguaje corporal o emoción (ej: "Sonrisa cálida", "Gesto de duda", "Señalando a la cámara").
"""

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
