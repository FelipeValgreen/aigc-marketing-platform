import streamlit as st
import requests
import json
import os

API_BASE_URL = os.getenv("API_BASE_URL", "https://valgreen21-aigc-backend.hf.space/api/v1")

st.set_page_config(page_title="Portal Agencia - AIGC", page_icon="⚙️", layout="wide")
st.title("⚙️ Dashboard de Agencia (Admin)")
st.markdown("Monitorea la Máquina de Estados de todos los proyectos en curso.")

if st.button("Actualizar Proyectos"):
    res = requests.get(f"{API_BASE_URL}/projects")
    if res.status_code == 200:
        projects = res.json()
        cols = st.columns((1, 1, 2, 2, 2, 2))
        cols[0].write("**ID**")
        cols[1].write("**Cliente**")
        cols[2].write("**Producto**")
        cols[3].write("**Ángulo**")
        cols[4].write("**Estado**")
        cols[5].write("**Acción**")
        
        for p in projects:
            c = st.columns((1, 1, 2, 2, 2, 2))
            c[0].write(p['id'])
            c[1].write(p['client_id'])
            c[2].write(p['product_name'])
            c[3].write(p.get('video_angle', '-'))
            if p['status'] == "COMPLETADO":
                c[4].success(p['status'])
            elif p['status'] == "GUION_LISTO":
                c[4].warning(p['status'])
            else:
                c[4].info(p['status'])
                
            with c[5]:
                if p.get('video_url'):
                    st.markdown(f"[Ver Video]({p['video_url']})")
                elif p.get('script_json'):
                    with st.popover("Ver Guion"):
                        try:
                            st.json(json.loads(p['script_json']))
                        except:
                            st.write(p['script_json'])
    else:
        st.error("Error cargando proyectos globales.")
