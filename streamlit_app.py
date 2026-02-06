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

# 2. CONTROL LATERAL
with st.sidebar:
    if st.button("Reiniciar Sistema"):
        st.session_state.messages = []
        st.rerun()

# 3. CONEXIÓN
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# 4. MEMORIA EQUILIBRADA
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres RUTH, una asistente sofisticada. Habla de forma elegante. Si el usuario pide una imagen, dibujo o foto, acepta la petición y al FINAL de tu respuesta de texto escribe SIEMPRE: 'DIBUJO: [descripción detallada en inglés]'."
        }
    ]

# Función para generar URL de imagen
def get_image_url(prompt_text):
    clean_prompt = prompt_text.replace("DIBUJO:", "").strip()
    prompt_enc = urllib.parse.quote(clean_prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{prompt_enc}?width=1024&height=1024&seed={seed}&nologo=true"

# 5. MOSTRAR CHAT
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
            # Si el mensaje tiene texto y comando de dibujo, separamos
            if "DIBUJO:" in msg["content"]:
                texto, comando = msg["content"].split("DIBUJO:", 1)
                if texto.strip(): st.markdown(texto)
                st.image(get_image_url(comando), use_container_width=True)
            else:
                st.markdown(msg["content"])

# 6. INTERACCIÓN
if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # Llamada a la IA
            response = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
            
            # Lógica Inteligente: ¿El usuario pidió una imagen?
            user_pide_imagen = any(x in prompt.lower() for x in ["imagen", "dibujo", "foto", "dibuja", "crea"])
            
            if user_pide_imagen and "DIBUJO:" not in response:
                # Si la IA olvidó el comando pero el usuario pidió imagen, se lo añadimos
                response += f"\n\nDIBUJO: {prompt}"

            # Mostrar resultado
            if "DIBUJO:" in response:
                texto, comando = response.split("DIBUJO:", 1)
                if texto.strip(): st.markdown(texto)
                st.image(get_image_url(comando), use_container_width=True)
            else:
                st.markdown(response)
                
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
