import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import urllib.parse
import random

# --- 1. CONFIGURACIÓN VISUAL (ESTO CARGA PRIMERO) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="centered")

# CSS Profesional: Fondo, Patrón, Título y Subtítulo
st.markdown("""
    <style>
    /* Fondo Oscuro con Patrón de puntos */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Ocultar elementos de Streamlit que molestan */
    footer {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none;}

    /* Título RUTH en ROJO */
    .ruth-header {
        text-align: center; padding-top: 1rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem; margin-bottom: 0px;
    }
    
    /* Subtítulo Profesional */
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.9rem; 
        letter-spacing: 0.2rem; margin-top: -10px; margin-bottom: 2rem;
    }
    
    /* Color de texto claro */
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</div>
""", unsafe_allow_html=True)

# --- 2. BOTÓN DE REINICIO (VISIBLE EN LA BARRA LATERAL) ---
with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    if st.button("🔄 NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Estado: Conectada a Internet (Feb 2026)")

# --- 3. LÓGICA DE BÚSQUEDA ---
def buscar_web(query):
    try:
        with DDGS() as ddgs:
            # Buscamos noticias recientes
            results = ddgs.text(query, max_results=3)
            if results:
                resumen = "\n".join([f"- {r['body']}" for r in results])
                return resumen
    except Exception:
        return None
    return None

# --- 4. CONEXIÓN CON GROQ ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Error: Falta la API Key en Settings > Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Memoria del chat
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []

# --- 5. MOSTRAR EL CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

# --- 6. ENTRADA DE USUARIO Y PROCESAMIENTO ---
if prompt := st.chat_input("Escribe tu consulta profesional..."):
    # Guardamos y mostramos mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de RUTH
    with st.chat_message("assistant", avatar=ruth_avatar):
        # ¿Necesita buscar en internet? (Detección simple)
        palabras_actualidad = ["pasó", "noticia", "hoy", "enero", "febrero", "2026", "actualmente", "precio"]
        contexto_web = ""
        
        if any(x in prompt.lower() for x in palabras_actualidad):
            with st.spinner("Investigando en tiempo real..."):
                contexto_web = buscar_web(prompt)
        
        try:
            # Construcción de la respuesta
            system_prompt = "Eres RUTH, una IA profesional. Si se te da información de internet, úsala para ser precisa."
            full_prompt = prompt
            if contexto_web:
                full_prompt = f"DATOS DE INTERNET:\n{contexto_web}\n\nPREGUNTA: {prompt}"

            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error de conexión: {e}")
