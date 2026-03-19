import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Onboarding - AIGC", page_icon="🏢")

st.title("🏢 Registro y Extracción de ADN de Marca")
st.markdown("Ingresa los datos para que nuestra IA audite tu marca y extraiga su identidad visual y semántica.")

with st.form("onboarding_form"):
    company_name = st.text_input("Nombre de la Empresa", placeholder="Ej. Hormiglass")
    website_url = st.text_input("URL del Sitio Web", placeholder="https://www.hormiglass.cl")
    submit_btn = st.form_submit_button("Auditar y Extraer ADN")
    
if submit_btn:
    if not company_name or not website_url:
        st.warning("Completa todos los campos.")
    else:
        with st.spinner("🕵️‍♂️ Scraping web y analizando con Gemini... (esto puede tomar un minuto)"):
            try:
                response = requests.post(f"{API_BASE_URL}/onboarding", json={
                    "company_name": company_name,
                    "website_url": website_url
                }, timeout=120)
                
                if response.status_code == 201:
                    data = response.json()
                    c_id = data['client']['id']
                    st.success(f"✅ ¡Cliente registrado con éxito! Tu ID asignado es: **{c_id}**")
                    
                    st.markdown("### 🧬 ADN de Marca Extraído")
                    gl = data['guidelines']
                    st.info(f"**Tono de Voz:** {gl.get('tone_of_voice')}")
                    st.warning(f"**Público Objetivo:** {gl.get('target_audience')}")
                    st.success(f"**Propuesta de Valor:** {gl.get('value_proposition')}")
                    st.error(f"**Color Principal (HEX):** {gl.get('primary_color_hex', '#FFFF00')}")
                    
                    st.markdown(f"**⚠️ IMPORTANTE:** Guarda tu ID de Cliente ({c_id}). Lo necesitarás en el Portal del Cliente para iniciar generacion de contenido.")
                else:
                    st.error(f"Error {response.status_code}: {response.json().get('detail', response.text)}")
            except Exception as e:
                st.error(f"Error de conexión con el backend: {str(e)}")
