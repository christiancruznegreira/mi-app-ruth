import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# 1. ESTÉTICA PREMIUM (NEGRA CON PUNTOS)
st.set_page_config(page_title="RUTH", page_icon="●")
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}
    .ruth-header {text-align: center; padding-top: 2rem; letter-spacing: 0.8rem; font-weight: 200; color: #ffffff; font-size: 3rem;}
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    </style>
    <div class="ruth-header">R U T H</div>
""", unsafe_allow_html=True)

# 2. BARRA LATERAL
with st.sidebar:
    if st.button("Reiniciar Sistema"):
        st.session_state.messages = []
        st.rerun()

# 3. CONEXIÓN
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# 4. MEMORIA REPROGRAMADA
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres RUTH. REGLA DE ORO: Si te piden una imagen, dibujo o foto, responde SOLAMENTE con la palabra 'DIBUJO:' y la descripción en inglés. Ejemplo: 'DIBUJO: a red car'. No digas nada más."
        }
    ]

# Función de imagen
def mostrar_imagen(texto_ia):
    prompt_puro = texto_ia.replace("DIBUJO:", "").strip()
    prompt_enc = urllib.parse.quote(prompt_puro)
    seed = random.randint(1, 100000)
    url = f"https://image.pollinations.ai/prompt/{prompt_enc}?width=1024&height=1024&seed={seed}&nologo=true"
    st.image(url, caption=f"RUTH Visual: {prompt_puro}", use_container_width=True)

# 5. MOSTRAR CHAT
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
            if "DIBUJO:" in msg["content"]:
                mostrar_imagen(msg["content"])
            else:
                st.markdown(msg["content"])

# 6. INTERACCIÓN
if prompt := st.chat_input("¿Qué ordenes tienes para RUTH?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # Forzamos a que piense que SÍ puede hacer imágenes
            respuesta_ia = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
            
            if "DIBUJO:" in respuesta_ia or "dibujo" in prompt.lower() or "imagen" in prompt.lower():
                # Si la IA se resiste pero el usuario pidió imagen, forzamos el formato
                if "DIBUJO:" not in respuesta_ia:
                    respuesta_ia = f"DIBUJO: {prompt}"
                
                mostrar_imagen(respuesta_ia)
            else:
                st.markdown(respuesta_ia)
                
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        except Exception as e:
            st.error(f"Error: {e}")
