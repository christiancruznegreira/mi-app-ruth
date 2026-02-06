import streamlit as st
from groq import Groq
import os
import urllib.parse

# 1. Configuración básica
st.set_page_config(page_title="RUTH", page_icon="●")

# 2. Título minimalista
st.markdown("<h1 style='text-align: center; font-weight: 200;'>R U T H</h1>", unsafe_allow_html=True)

# 3. Configuración del Logo
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# 4. Conexión de seguridad
if "GROQ_API_KEY" not in st.secrets:
    st.error("Falta la llave API.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

# 5. Memoria del Chat y Habilidades
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres RUTH, una asistente de IA elegante. HABILIDAD ESPECIAL: Si el usuario te pide una imagen o dibujo, DEBES responder ÚNICAMENTE con la palabra 'GENERANDO_IMAGEN:' seguido de una descripción corta y detallada en inglés de lo que el usuario quiere. Ejemplo: 'GENERANDO_IMAGEN: a minimalist landscape with mountains'."
        }
    ]

# 6. Mostrar el historial
for message in st.session_state.messages:
    if message["role"] != "system":
        # Si el mensaje contiene la instrucción de imagen, la mostramos
        if "GENERANDO_IMAGEN:" in message["content"]:
            prompt_imagen = message["content"].replace("GENERANDO_IMAGEN:", "").strip()
            with st.chat_message("assistant", avatar=ruth_avatar):
                st.write(f"He creado esta imagen para ti sobre: *{prompt_imagen}*")
                # Generador gratuito Pollinations
                url_final = f"https://pollinations.ai/p/{urllib.parse.quote(prompt_imagen)}?width=1024&height=1024&seed=42&nologo=true"
                st.image(url_final, use_container_width=True)
        else:
            av = ruth_avatar if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=av):
                st.markdown(message["content"])

# 7. Entrada de usuario
if prompt := st.chat_input("¿Qué necesitas?"):
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
            
            # Lógica para mostrar la imagen inmediatamente
            if "GENERANDO_IMAGEN:" in response:
                prompt_imagen = response.replace("GENERANDO_IMAGEN:", "").strip()
                st.write("Generando tu imagen personalizada...")
                url_final = f"https://pollinations.ai/p/{urllib.parse.quote(prompt_imagen)}?width=1024&height=1024&seed=42&nologo=true"
                st.image(url_final, use_container_width=True)
            else:
                st.markdown(response)
                
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
