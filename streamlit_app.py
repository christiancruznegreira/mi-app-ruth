import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS # Nueva herramienta de búsqueda
import os
import urllib.parse
import random

# --- CONFIGURACIÓN ESTÉTICA (NEGRO Y ROJO) ---
st.set_page_config(page_title="RUTH Intelligence", page_icon="●")
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; background-image: radial-gradient(#1a1d24 1px, transparent 1px); background-size: 30px 30px; }
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}
    .ruth-header { text-align: center; padding-top: 2rem; letter-spacing: 0.8rem; font-weight: 200; color: #ff4b4b; font-size: 3.5rem; }
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    </style>
    <div class="ruth-header">R U T H</div>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE BÚSQUEDA EN TIEMPO REAL ---
def buscar_en_internet(query):
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(query, max_results=3)]
            contexto = "\n".join([f"Fuente: {r['body']}" for r in resultados])
            return contexto
    except Exception:
        return "No pude conectar a internet en este momento."

# --- LÓGICA DE IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Reiniciar Sistema"):
        st.session_state.messages = []
        st.rerun()

# --- INTERACCIÓN ---
if prompt := st.chat_input("Consulta a RUTH..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        # 1. ¿Necesita buscar en internet? 
        # Si el usuario pregunta por fechas recientes o noticias
        if any(palabra in prompt.lower() for palabra in ["pasó", "noticias", "hoy", "enero", "2026", "actualmente"]):
            with st.spinner("RUTH está consultando fuentes globales..."):
                informacion_actualizada = buscar_en_internet(prompt)
                prompt_mejorado = f"Información de internet: {informacion_actualizada}\n\nPregunta del usuario: {prompt}"
        else:
            prompt_mejorado = prompt

        try:
            # 2. RUTH procesa la información
            # Usamos un mensaje de sistema dinámico para darle contexto profesional
            mensajes_con_contexto = [
                {"role": "system", "content": "Eres RUTH, una IA profesional con acceso a internet. Usa la información proporcionada para dar respuestas precisas y actualizadas."},
                {"role": "user", "content": prompt_mejorado}
            ]
            
            completion = client.chat.completions.create(
                messages=mensajes_con_contexto,
                model="llama-3.3-70b-versatile",
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
