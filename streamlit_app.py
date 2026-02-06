import streamlit as st
from groq import Groq

# Configuración de página minimalista
st.set_page_config(page_title="RUTH", page_icon="●")

st.markdown("<h1 style='text-align: center; font-weight: 200;'>R U T H</h1>", uunsafe_allow_html=True)

# Conexión con la llave que obtuviste en el paso 1
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres RUTH, una IA minimalista y elegante."}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("¿Qué necesitas?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
