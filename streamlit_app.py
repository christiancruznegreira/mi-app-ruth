import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os

# --- 1. BRANDING Y ESTÉTICA (CARGA TOTALMENTE INDEPENDIENTE) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    footer {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none;}
    .ruth-header {
        text-align: center; padding-top: 1rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem; margin-bottom: 0px;
    }
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.9rem; 
        letter-spacing: 0.2rem; margin-top: -10px; margin-bottom: 2rem;
    }
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</div>
""", unsafe_allow_html=True)

# --- 2. BARRA LATERAL (SIEMPRE VISIBLE) ---
with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    if st.button("🔄 NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Conexión: Red Global RUTH (Activa)")

# --- 3. FUNCIÓN DE BÚSQUEDA ---
def buscar_web(query):
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(query, max_results=4)]
            if resultados:
                return "\n\n".join([f"NOTICIA: {r['body']}" for r in resultados])
    except:
        return None
    return None

# --- 4. CONFIGURACIÓN DE IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

# --- 5. INTERACCIÓN Y LÓGICA DE ACTUALIDAD ---
if prompt := st.chat_input("Consulta a RUTH Professional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        contexto_web = ""
        # Detectar si pregunta por fechas de 2024, 2025 o 2026
        if any(x in prompt.lower() for x in ["2024", "2025", "2026", "hoy", "pasó", "enero", "febrero", "noticia"]):
            with st.spinner("Investigando fuentes en tiempo real..."):
                contexto_web = buscar_web(prompt)
        
        try:
            # INSTRUCCIÓN MAESTRA: PROHIBIDO DECIR QUE NO TIENE ACCESO
            system_instruction = (
                "Eres RUTH. Tu conocimiento llega hasta hoy, 6 de febrero de 2026. "
                "Si se te proporciona información bajo el título 'DATOS DE INTERNET', "
                "ÚSALA obligatoriamente para responder. NO digas que no tienes acceso a tiempo real. "
                "Tu objetivo es ser una asistente profesional actualizada."
            )
            
            if contexto_web:
                mensaje_para_ia = f"DATOS DE INTERNET PARA RESPONDER:\n{contexto_web}\n\nPREGUNTA DEL USUARIO: {prompt}"
            else:
                mensaje_para_ia = prompt

            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": mensaje_para_ia}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
