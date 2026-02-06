import streamlit as st
from groq import Groq
from googlesearch import search # Nueva herramienta de Google
import os
import urllib.parse
import random

# --- 1. BRANDING Y ESTÉTICA (CARGA PRIORITARIA) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    footer {visibility: hidden;}
    .viewerBadge_container__1QS1n {display: none;}

    .ruth-header {
        text-align: center; padding-top: 1rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem; margin-bottom: 0px;
    }
    
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.9rem; 
        letter-spacing: 0.2rem; margin-top: -10px; margin-bottom: 2rem;
    }
    
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</div>
""", unsafe_allow_html=True)

# --- 2. BOTÓN DE REINICIO EN BARRA LATERAL ---
# Nota: Si no ves la barra lateral, busca una flechita ">" arriba a la izquierda
with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    if st.button("🔄 NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Conexión: Google Search Cloud (Gratis)")

# --- 3. LÓGICA DE BÚSQUEDA EN GOOGLE ---
def buscar_en_google(query):
    try:
        # Buscamos en Google y extraemos los primeros 3 resultados
        resultados = []
        # Buscamos con un lenguaje específico para 2026
        for j in search(query, num_results=3, lang="es", advanced=True):
            resultados.append(f"Título: {j.title}\nDescripción: {j.description}")
        
        return "\n\n".join(resultados) if resultados else None
    except Exception:
        return None

# --- 4. CONFIGURACIÓN DE IA ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Error: Falta la API Key en los Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

# --- 6. INTERACCIÓN ---
if prompt := st.chat_input("Consulta a RUTH Professional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        # Detectar si la pregunta requiere datos actuales (noticias, fechas, etc.)
        palabras_clave = ["pasó", "noticia", "hoy", "enero", "febrero", "2026", "quién es", "precio"]
        contexto_google = ""
        
        if any(x in prompt.lower() for x in palabras_clave):
            with st.spinner("RUTH está consultando Google..."):
                contexto_google = buscar_en_google(prompt)
        
        try:
            # Si Google nos dio información, se la pasamos a la IA
            if contexto_google:
                mensaje_final = f"DATOS ENCONTRADOS EN GOOGLE:\n{contexto_google}\n\nPREGUNTA: {prompt}"
            else:
                mensaje_final = prompt

            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres RUTH, una IA profesional. Usa la información de Google para responder con precisión sobre eventos actuales de 2026."},
                    {"role": "user", "content": mensaje_final}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error de conexión: {e}")
