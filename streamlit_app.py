import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# --- ESTÉTICA PREMIUM NEGRA Y ROJA ---
st.set_page_config(page_title="RUTH Intelligence", page_icon="●", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}
    .ruth-header {text-align: center; padding-top: 2rem; letter-spacing: 0.8rem; font-weight: 200; color: #ff4b4b; font-size: 4rem;}
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important; font-size: 1.1rem;}
    
    /* Estilo de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #161a21;
        border-right: 1px solid #333;
    }
    </style>
    <div class="ruth-header">R U T H</div>
    <p style='text-align: center; color: #888; font-size: 0.9rem; margin-top: -1.5rem; letter-spacing: 0.3rem;'>UNIVERSAL PROFESSIONAL INTELLIGENCE</p>
""", unsafe_allow_html=True)

# --- PANEL DE CONTROL PROFESIONAL ---
with st.sidebar:
    st.markdown("### 🛠 Perfil del Profesional")
    profesion = st.text_input("¿Cuál es tu profesión?", placeholder="Ej: Abogado Penalista, Arquitecto...")
    objetivo = st.text_area("¿Cuál es tu objetivo hoy?", placeholder="Ej: Redactar contratos, diseñar planos...")
    
    st.divider()
    if st.button("Reiniciar Sesión Inteligente"):
        st.session_state.messages = []
        st.rerun()

# --- CEREBRO DE RUTH ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Instrucciones Universales de RUTH
sys_message = (
    f"Tu nombre es RUTH. Eres una Inteligencia de Grado Profesional. "
    f"Te estás comunicando con un {profesion if profesion else 'Profesional experto'}. "
    f"Tu objetivo actual es: {objetivo if objetivo else 'Asistir en tareas de alta complejidad'}. "
    "Tu tono es ejecutivo, preciso y de altísimo nivel. No usas lenguaje infantil. "
    "Si el usuario pide un análisis, dáselo con estructura de puntos. "
    "Si pide una imagen técnica, responde con DIBUJO: [descripción]."
)

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [{"role": "system", "content": sys_message}]

# --- INTERFAZ DE TRABAJO ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        av = ruth_avatar if msg["role"]=="assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input("Ingresa tu requerimiento profesional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # Actualizamos el sistema con la profesión actual antes de cada mensaje
            st.session_state.messages[0]["content"] = sys_message
            
            completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error de sistema: {e}")
