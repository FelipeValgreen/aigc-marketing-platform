import streamlit as st
import requests
import json
import os

API_BASE_URL = os.getenv("API_BASE_URL", "https://valgreen21-aigc-backend.hf.space/api/v1")

st.set_page_config(page_title="Portal Cliente - AIGC", page_icon="👤", layout="wide")
st.title("👤 Portal del Cliente")
st.markdown("Bienvenido a tu creador de contenido paso a paso.")

client_id_val = st.number_input("ID de tu Marca (Cliente)", min_value=1, step=1)

tabs = st.tabs(["🛣️ Nuevo Proyecto (Paso a Paso)", "🗄️ Mis Proyectos (Bóveda)"])

with tabs[0]:
    st.header("Paso 1: Briefing y Estrategia")
    with st.form("project_form"):
        prod_name = st.text_input("Nombre del Producto/Servicio")
        prod_desc = st.text_area("Descripción detallada")
        angle = st.selectbox("Ángulo Estratégico del Video", [
            "Educativo/Concientización", 
            "Storytelling + Voice Over", 
            "Hook + Producto", 
            "UGC + Producto", 
            "UGC Tradicional", 
            "Hard Selling"
        ])
        music_style = st.selectbox("Estilo de Música de Fondo", ["Sin Música", "Upbeat (Dinámico)", "Corporativo (Serio)", "Lo-Fi (Relajado)"])
        uploaded_media = st.file_uploader("📥 Sube tu propia imagen o video base (Opcional)", type=['mp4', 'mov', 'jpg', 'png'])
        submit_brief = st.form_submit_button("Generar Guiones")
        
    if submit_brief and prod_name:
        with st.spinner("Creando proyecto y extrayendo ángulos..."):
            data = {
                "client_id": client_id_val,
                "product_name": prod_name,
                "product_desc": prod_desc,
                "video_angle": angle,
                "music_style": music_style
            }
            files = None
            if uploaded_media:
                files = {"custom_media": (uploaded_media.name, uploaded_media.getvalue(), uploaded_media.type)}
                
            res = requests.post(f"{API_BASE_URL}/projects", data=data, files=files)
            
            if res.status_code == 201:
                st.session_state['current_project'] = res.json()
                st.success("¡Guiones generados exitosamente!")
            else:
                st.error(f"Error: {res.text}")

    if 'current_project' in st.session_state:
        proj = st.session_state['current_project']
        if proj.get('status') == 'GUION_LISTO':
            st.divider()
            st.header("Paso 2: Aprobación de Guión")
            try:
                script_data = proj['script'] if isinstance(proj['script'], dict) else json.loads(proj['script'])
                st.json(script_data)
            except:
                st.write(proj['script'])
            
            if st.button("✅ Aprobar y Mandar a Producción", use_container_width=True, type="primary"):
                with st.spinner("Ensamblando video (Voz, Subtítulos dinámicos, B-Roll)..."):
                    res = requests.post(f"{API_BASE_URL}/projects/{proj['project_id']}/approve-and-render")
                    if res.status_code == 200:
                        st.success("¡Video producido exitosamente!")
                        st.session_state['current_project']['status'] = 'COMPLETADO'
                        st.session_state['current_project']['video_url'] = res.json().get('video_url')
                        st.rerun()
                    else:
                        st.error(f"Error en renderizado: {res.text}")
                        
        if proj.get('status') == 'COMPLETADO':
            st.divider()
            st.header("Paso 3: Entrega Final")
            st.video(proj['video_url'])
            st.balloons()

with tabs[1]:
    st.header("🗄️ Bóveda de Contenido")
    if st.button("Cargar Mis Proyectos"):
        res = requests.get(f"{API_BASE_URL}/clients/{client_id_val}/projects")
        if res.status_code == 200:
            projects = res.json()
            for p in projects:
                with st.expander(f"{p['product_name']} - Estado: {p['status']} ({p.get('video_angle', '')})"):
                    if p['status'] == 'COMPLETADO' and p.get('video_url'):
                        st.video(p['video_url'])
                    elif p.get('script_json'):
                        try:
                            st.json(json.loads(p['script_json']))
                        except:
                            st.write(p['script_json'])
        else:
            st.error("Error cargando bóveda.")
