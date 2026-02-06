import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# 1. CONFIGURACIÓN PREMIUM
st.set_page_config(page_title="RUTH", page_icon="●", layout="centered")

# CSS Avanzado para Estética Minimalista y Premium
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none;}
    
    /* Fondo y Tipografía General */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Estilo del Título Central */
    .ruth-header {
        text-align: center;
        padding-top: 3rem;
        padding-bottom: 2rem;
        letter-spacing: 0.5rem;
        font-weight: 200;
        color: #1a1a1a;
        font-size: 2.5rem;
    }

    /* Contenedor de mensajes */
    .stChatMessage {
        background-color: transparent !important;
        border-bottom: 1px solid #f0f0f0 !important;
        padding: 1.5rem 0.5rem !important;
        border-radius: 0px !important;
    }

    /* Avatar personalizado */
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #000 !important;
        border: 1px solid #333;
    }

    /* Caja de entrada de texto */
    .stChatInputContainer {
        border-top: none !important;
        padding-bottom: 3rem !important;
    }
    
    .stChatInput {
        border-radius: 50px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: #fafafa !important;
    }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <p style='text-align: center; color: #888; letter-spacing: 0.2rem; font-size: 0.7rem; margin-top: -1.5rem; margin-bottom: 2rem;'>
        INTELLIGENT ASSISTANCE
    </p>
""", unsafe_allow_html=True)

# 2. LÓGICA DE BACKEND (GROQ)
with st.sidebar:
    st.markdown("### Configuración")
    if st.button("Limpiar Memoria"):
        st.session_state.messages = []
        st.rerun()

icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "GROQ_API_KEY" not in st.secrets:
    st.error("Falta la llave API.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": "Eres RUTH. Tu tono es sofisticado, minimalista y extremadamente útil."}
    ]

# Función para imágenes
def get_image_url(prompt_text):
    prompt_encoded = urllib.parse.quote(prompt_text)
    return f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"

# 3. CHAT
for message in st.session_state.messages:
    if message["role"] != "system":
        av = ruth_avatar if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=av):
            if "GENERANDO_IMAGEN:" in message["content"]:
                prompt_img = message["content"].replace("GENERANDO_IMAGEN:", "").strip()
                st.image(get_image_url(prompt_img), use_container_width=True)
            else:
                st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu consulta..."):
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
                st.image(get_image_url(prompt_img), use_container_width=True)
            else:
                st.markdown(response)
                
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
