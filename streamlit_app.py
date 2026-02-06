import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import urllib.parse
import random

# --- 1. CONFIGURACIÓN VISUAL PREMIM (ESTÉTICA DE LUJO) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="centered")

st.markdown("""
    <style>
    /* Fondo Negro con Patrón de puntos sutiles */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}

    /* Título RUTH en ROJO con GLOW */
    .ruth-header {
        text-align: center; 
        padding-top: 2rem; 
        letter-spacing: 0.8rem; 
        font-weight: 200; 
        color: #ff4b4b; 
        font-size: 3.5rem;
        text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.2);
        margin-bottom: 0px;
    }
    
    /* Subtítulo Profesional Minimalista */
    .ruth-subtitle {
        text-align: center; 
        color: #888; 
        font-size: 0.8rem; 
        margin-top: -10px; 
        letter-spacing: 0.3rem; 
        margin-bottom: 3rem;
        font-weight: bold;
    }
    
    /* Burbujas de chat elegantes */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 10px !important;
    }

    /* Color de texto claro */
    div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Input de texto minimalista */
    .stChatInputContainer {
        padding-bottom: 2rem !important;
    }
    .stChatInput {
        background-color: #1a1d24 !important;
        border-radius: 20px !important;
        border: 1px solid #333 !important;
    }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</div>
""", unsafe_allow_html=True)

# --- 2. BARRA LATERAL (CONTROL) ---
with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    if st.button("🔄 NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Estado: Conexión Global Activa")

# --- 3. LÓGICA DE BÚSQUEDA WEB ---
def buscar_web(query):
    try:
        with DDGS() as ddgs:
            # Buscamos noticias específicas de 2026
            results = ddgs.text(f"{query} noticias 2026", max_results=3)
            if results:
                return "\n\n".join([f"- {r['body']}" for r in results])
    except Exception:
        return None
    return None

# --- 4. CONFIGURACIÓN DE IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial del chat
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# --- 5. INTERACCIÓN Y RESPUESTA ---
if prompt := st.chat_input("Escribe tu requerimiento profesional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        # ¿Es una pregunta de actualidad?
        palabras_actualidad = ["pasó", "noticia", "enero", "febrero", "2026", "hoy", "quién es"]
        contexto_web = ""
        
        if any(x in prompt.lower() for x in palabras_actualidad):
            with st.spinner("Investigando en tiempo real..."):
                contexto_web = buscar_web(prompt)

        # Instrucción Maestra para forzar la actualidad
        fecha_actual = "Viernes 6 de Febrero de 2026"
        instruccion = f"Tu nombre es RUTH. Hoy es {fecha_actual}. Eres una IA profesional avanzada. "
        
        if contexto_web:
            instruccion += f"Aquí tienes DATOS REALES DE INTERNET para responder: {contexto_web}. PROHIBIDO decir que no tienes acceso a internet. Responde usando estos datos."
        else:
            instruccion += "Responde con profesionalismo y elegancia."

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
