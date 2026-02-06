import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import urllib.parse
import random

# 1. CONFIGURACIÓN VISUAL (LO PRIMERO QUE CARGA)
st.set_page_config(page_title="RUTH Professional", page_icon="●")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .ruth-title { text-align: center; color: #ff4b4b; font-size: 4rem; letter-spacing: 0.5rem; margin-bottom: 0; }
    .ruth-sub { text-align: center; color: #888; font-size: 1rem; margin-top: -10px; font-weight: bold; }
    </style>
    <h1 class="ruth-title">R U T H</h1>
    <p class="ruth-sub">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</p>
""", unsafe_allow_html=True)
st.divider()

# 2. BARRA LATERAL CON BOTÓN DE REINICIO
with st.sidebar:
    st.header("SISTEMA")
    if st.button("🗑️ REINICIAR CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()

# 3. LÓGICA DE BÚSQUEDA WEB
def realizar_busqueda(consulta):
    try:
        with DDGS() as ddgs:
            # Buscamos noticias específicas de 2026
            resultados = ddgs.text(f"{consulta} 2026", max_results=3)
            if resultados:
                return "\n".join([f"- {r['body']}" for r in resultados])
    except Exception:
        return None
    return None

# 4. CONEXIÓN CON LA IA
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial del chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. ENTRADA DE USUARIO Y RESPUESTA INTELIGENTE
if prompt := st.chat_input("Escribe tu consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ¿Necesitamos buscar en internet?
        palabras_web = ["pasó", "noticia", "enero", "2026", "actualidad", "quién es"]
        contexto_web = ""
        
        if any(x in prompt.lower() for x in palabras_web):
            with st.spinner("RUTH consultando fuentes globales..."):
                contexto_web = realizar_busqueda(prompt)

        # Construimos la instrucción maestra para la IA
        fecha_hoy = "Viernes 6 de Febrero de 2026"
        instruccion = f"Eres RUTH, una IA profesional. Hoy es {fecha_hoy}. "
        
        if contexto_web:
            instruccion += f"Usa estos datos reales de internet para responder: {contexto_web}. "
        else:
            instruccion += "Responde con tu conocimiento base pero mantén tu identidad de 2026."

        try:
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": instruccion},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
            
            respuesta = completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error técnico: {e}")
