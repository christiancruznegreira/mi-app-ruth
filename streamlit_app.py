import streamlit as st
from groq import Groq

# Configuración de página
st.set_page_config(page_title="RUTH", page_icon="logo_ruth.png")

# Título
st.markdown("<h1 style='text-align: center; font-weight: 200;'>R U T H</h1>", unsafe_allow_html=True)

# Verificación de seguridad
if "GROQ_API_KEY" not in st.secrets:
    st.error("Error: Configura la llave en los Secrets de Streamlit.")
    st.stop()

# Limpieza de la llave
api_key_limpia = st.secrets["GROQ_API_KEY"].strip()
client = Groq(api_key=api_key_limpia)

# Memoria de RUTH
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres RUTH, una asistente de IA minimalista, elegante y profesional."}]

# Mostrar chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Qué necesitas?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Modelo potente y actual (Febrero 2026)
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"RUTH tiene un problema técnico: {e}")
