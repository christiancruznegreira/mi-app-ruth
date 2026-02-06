import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RUTH", page_icon="●", layout="centered")

# CSS para MODO OSCURO PREMIUM CON PATRÓN
st.markdown("""
    <style>
    /* Fondo Oscuro con Patrón sutil */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px; /* Este crea el patrón de puntos elegantes */
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none;}

    /* Título RUTH elegante */
    .ruth-header {
        text-align: center;
        padding-top: 2rem;
        letter-spacing: 0.8rem;
        font-weight: 200;
        color: #ffffff;
        font-size: 3rem;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.1);
    }

    /* Mensajes de Chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Input de texto */
    .stChatInput {
        background-color: #1a1d24 !important;
        border: 1px solid #333 !important;
        border-radius: 15px !important;
    }
    
    /* Forzar texto blanco */
    div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
    }
    </style>
    
    <div class="ruth-header">R U T H</div>
""", unsafe_allow_html=True)

# 2. LOGICA
with st.sidebar:
    st.markdown("### Control")
    if st.button("Reiniciar Chat"):
        st.session_state.messages = []
        st.rerun()

icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "GROQ_API_KEY" not in st.secrets:
    st.error("Error: Llave no configurada.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": "Eres RUTH. Tu tono es sofisticado y minimalista. Si piden imagen, usa: GENERANDO_IMAGEN: description."}
    ]

def get_image_url(prompt_text):
    prompt_encoded = urllib.parse.quote(prompt_text)
    seed = random.randint(1, 9999)
    return f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&seed={seed}&nologo=true"

# 3. INTERFAZ DE CHAT
for message in st.session_state.messages:
    if message["role"] != "system":
        av = ruth_avatar if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=av):
            if "GENERANDO_IMAGEN:" in message["content"]:
                prompt_img = message["content"].replace("GENERANDO_IMAGEN:", "").strip()
                st.image(get_image_url(prompt_img), use_container_width=True)
            else:
                st.markdown(message["content"])

if prompt := st.chat_input("¿Qué necesitas de RUTH?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            )
            response = completion.choices[0].message.content
            
            if "GENERANDO_IMAGEN:" in response:
                prompt_img = response.replace("GENERANDO_IMAGEN:", "").strip()
                st.image(get_image_url(prompt_img), use_container_width
