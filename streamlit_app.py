import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RUTH", page_icon="●", layout="centered")

# 2. ESTÉTICA OSCURA PREMIUM CON PATRÓN
st.markdown("""
    <style>
    /* Fondo Oscuro con Patrón de puntos sutiles */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Ocultar elementos de la interfaz de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none;}

    /* Título RUTH minimalista */
    .ruth-header {
        text-align: center;
        padding-top: 2rem;
        letter-spacing: 0.8rem;
        font-weight: 200;
        color: #ffffff;
        font-size: 3rem;
        text-shadow: 0px 0px 10px rgba(255,255,255,0.1);
    }

    /* Estilo de los mensajes */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Caja de entrada de texto */
    .stChatInput {
        background-color: #1a1d24 !important;
        border: 1px solid #333 !important;
        border-radius: 15px !important;
    }

    /* Color de texto general */
    div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
    }
    </style>
    
    <div class="ruth-header">R U T H</div>
""", unsafe_allow_html=True)

# 3. LÓGICA DE CONTROL (BARRA LATERAL)
with st.sidebar:
    st.markdown("### Centro de Control")
    if st.button("Reiniciar Conversación"):
        st.session_state.messages = []
        st.rerun()

# Carga de icono personalizado
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Verificación de API Key
if "GROQ_API_KEY" not in st.secrets:
    st.error("Error: Configure su API Key en los Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

# Inicialización de memoria
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": "Eres RUTH. Tu tono es sofisticado y minimalista. Si el usuario pide una imagen, responde con: GENERANDO_IMAGEN: description."}
    ]

# Función para generar la URL de la imagen
def get_image_url(prompt_text):
    prompt_encoded = urllib.parse.quote(prompt_text)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&seed={
