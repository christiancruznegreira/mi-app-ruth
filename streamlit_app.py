import streamlit as st
from groq import Groq
import os

# 1. CONFIGURACIÓN VISUAL (Mantenemos tu Neón Rojo)
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #ff0000, 0 0 11px #ff0000, 0 0 40px #ff4b4b;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; letter-spacing: 1.5rem; font-weight: 100; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; }
    </style>
    <div class="ruth-header">R U T H</div>
""", unsafe_allow_html=True)

# 2. LÓGICA DE IMAGEN DINÁMICA
# Diccionario que asocia el MODO con la IMAGEN
MAPA_RUTH = {
    "Abogada": "ruth_lawyer.png",
    "Amazon Pro": "ruth_amazon.png",
    "Marketing": "ruth_thinking.png", # Puedes usar thinking o crear una de marketing
    "Estratega": "ruth_ceo.png"
}

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    # Selector de Modo (Cambia la imagen automáticamente)
    modo = st.selectbox("Identidad de RUTH:", list(MAPA_RUTH.keys()))
    
    # Mostramos la imagen correspondiente al modo
    imagen_actual = MAPA_RUTH[modo]
    if os.path.exists(imagen_actual):
        st.image(imagen_actual, use_container_width=True)
    else:
        # Imagen por defecto si no encuentra la otra
        st.image("ruth_normal.png", use_container_width=True)
    
    st.divider()
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()

# 4. LÓGICA DE CHAT (Mantenemos tu Groq estable)
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

if "messages" not in st.session_state: st.session_state.messages = []

# Mostrar Chat
for msg in st.session_state.messages:
    # Para el icono del chat usamos el logo de la R roja que ya tenías
    av = "logo_ruth.png" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="logo_ruth.png"):
        # Mensaje de sistema según el modo
        instruccion = f"Eres RUTH en modo {modo}. Sé directa y profesional."
        
        c = client.chat.completions.create(
            messages=[{"role":"system","content": instruccion}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
