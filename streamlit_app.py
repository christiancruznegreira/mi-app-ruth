import streamlit as st
from groq import Groq
import os

# 1. Configuración básica
st.set_page_config(page_title="RUTH", page_icon="●")

# 2. Título minimalista
st.markdown("<h1 style='text-align: center; font-weight: 200;'>R U T H</h1>", unsafe_allow_html=True)

# 3. Configuración del Logo (Avatar)
# Asegúrate de subir un archivo llamado 'logo_ruth.png' a tu GitHub
icon_path = "logo_ruth.png"
if os.path.exists(icon_path):
    ruth_avatar = icon_path
else:
    ruth_avatar = "●" # Si no encuentra la imagen, usa este punto negro

# 4. Conexión de seguridad
if "GROQ_API_KEY" not in st.secrets:
    st.error("Falta la llave GROQ_API_KEY en los Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

# 5. Memoria del Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres RUTH, una asistente de IA minimalista y elegante."}]

# 6. Mostrar el historial con iconos
for message in st.session_state.messages:
    if message["role"] != "system":
        # Si es la IA, usa el logo; si es el usuario, no usa icono
        av = ruth_avatar if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=av):
            st.markdown(message["content"])

# 7. Entrada de usuario y respuesta
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
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
