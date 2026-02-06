import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# 1. Configuración de página
st.set_page_config(page_title="RUTH", page_icon="●")

# 2. Título y Botón de Reinicio en la barra lateral
st.markdown("<h1 style='text-align: center; font-weight: 200;'>R U T H</h1>", unsafe_allow_html=True)

with st.sidebar:
    if st.button("Reiniciar Conversación"):
        st.session_state.messages = []
        st.rerun()

# 3. Configuración del Logo
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# 4. Conexión de seguridad
if "GROQ_API_KEY" not in st.secrets:
    st.error("Falta la llave API.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

# --- 5. MEMORIA Y REGLAS DE RUTH (REFORZADAS) ---
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "Tu nombre es RUTH. ERE OBLIGATORIO que sigas estas reglas: "
                "1. Eres capaz de generar imágenes. Si te piden una, NO digas que no puedes. "
                "2. Para generar imágenes, escribe ÚNICAMENTE: 'GENERANDO_IMAGEN: [descripción en inglés]'. "
                "3. No des explicaciones ni disculpas sobre ser un modelo de texto. "
                "4. Si te piden una imagen de algo, simplemente genera el comando."
            )
        }
    ]
# Función para crear el enlace de la imagen
def get_image_url(prompt_text):
    prompt_encoded = urllib.parse.quote(prompt_text)
    seed = random.randint(1, 100000)
    return f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&seed={seed}&nologo=true"

# 6. Mostrar el historial
for message in st.session_state.messages:
    if message["role"] != "system":
        if "GENERANDO_IMAGEN:" in message["content"]:
            prompt_img = message["content"].replace("GENERANDO_IMAGEN:", "").strip()
            with st.chat_message("assistant", avatar=ruth_avatar):
                st.image(get_image_url(prompt_img), caption=f"Imagen: {prompt_img}", use_container_width=True)
        else:
            av = ruth_avatar if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=av):
                st.markdown(message["content"])

# 7. Entrada de usuario
if prompt := st.chat_input("Escribe aquí..."):
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
