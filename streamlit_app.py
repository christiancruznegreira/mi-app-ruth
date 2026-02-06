import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import urllib.parse
import random

# 1. CONFIGURACIÓN DE PÁGINA Y ESTÉTICA PREMIUM
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="centered")

st.markdown("""
    <style>
    /* Fondo Oscuro con Patrón */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}

    /* Título RUTH en ROJO */
    .ruth-header {
        text-align: center; padding-top: 2rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem;
    }
    
    /* Subtítulo Profesional */
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.8rem; 
        margin-top: -1.5rem; letter-spacing: 0.2rem; margin-bottom: 2rem;
    }
    
    /* Color de texto */
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL PROFESSIONAL INTELLIGENCE</div>
""", unsafe_allow_html=True)

# 2. BARRA LATERAL (Botón de Nueva Conversación)
with st.sidebar:
    st.markdown("### Centro de Control")
    if st.button("🔄 Nueva Conversación"):
        st.session_state.messages = []
        st.rerun()
    st.info("Hoy es viernes, 6 de febrero de 2026. RUTH está operativa con acceso a internet.")

# 3. LÓGICA DE BÚSQUEDA REAL
def buscar_noticias(query):
    try:
        with DDGS() as ddgs:
            # Buscamos los 3 resultados más recientes
            search_results = [r for r in ddgs.text(query, max_results=3)]
            if not search_results:
                return "No encontré noticias recientes sobre esto."
            
            texto_resultados = "\n".join([f"- {r['body']} (Fuente: {r['href']})" for r in search_results])
            return texto_resultados
    except Exception as e:
        return f"Error en la búsqueda: {e}"

# 4. CONEXIÓN CON IA (GROQ)
if "GROQ_API_KEY" not in st.secrets:
    st.error("Configura la llave GROQ_API_KEY en los Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Memoria del chat
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "system", "content": "Eres RUTH, una inteligencia profesional de élite. Tienes acceso a internet para dar datos precisos de 2026."}
    ]

# 5. MOSTRAR CHAT
for msg in st.session_state.messages:
    if msg["role"] != "system":
        av = ruth_avatar if msg["role"]=="assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

# 6. ENTRADA DE USUARIO Y RESPUESTA
if prompt := st.chat_input("Consulta a RUTH Professional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        # ¿La pregunta requiere buscar en internet?
        detectar_actualidad = any(x in prompt.lower() for x in ["pasó", "noticia", "hoy", "enero", "febrero", "2026", "actualmente", "quién es"])
        
        contexto_web = ""
        if detectar_actualidad:
            with st.spinner("RUTH está investigando en la red..."):
                contexto_web = buscar_noticias(prompt)
        
        try:
            # Construimos la pregunta final para la IA
            pregunta_final = prompt
            if contexto_web:
                pregunta_final = f"CONTEXTO DE INTERNET RECIENTE:\n{contexto_web}\n\nPREGUNTA DEL USUARIO: {prompt}\n\nPor favor, responde usando los datos del contexto."

            completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "Eres RUTH. Responde de forma profesional."}, 
                          {"role": "user", "content": pregunta_final}],
                model="llama-3.3-70b-versatile",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
