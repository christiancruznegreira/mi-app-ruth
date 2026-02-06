import streamlit as st
from groq import Groq
import os

# --- 1. ESTÉTICA PREMIUM RUTH (ROJO Y NEGRO) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}
    .ruth-header {
        text-align: center; padding-top: 2rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem;
    }
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.8rem; 
        margin-top: -10px; letter-spacing: 0.3rem; margin-bottom: 3rem;
    }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</div>
""", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DEL CEREBRO GROQ (EL QUE SÍ FUNCIONA) ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Error: Falta GROQ_API_KEY en los Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Memoria del chat
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    if st.button("🔄 REINICIAR RUTH"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Cerebro: Llama 3 (Groq High Speed)")

# Mostrar historial
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# --- 3. INTERACCIÓN ---
if prompt := st.chat_input("Consulta a RUTH Professional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # Instrucción Maestra para que RUTH sea útil hoy
            system_prompt = (
                "Eres RUTH, una asistente de IA profesional y sofisticada. "
                "Hoy es viernes 6 de febrero de 2026. "
                "Aunque no tengas búsqueda web en este momento, eres experta en negocios, leyes e inmobiliaria. "
                "Responde siempre con elegancia y precisión profesional."
            )
            
            # Combinamos el historial con la instrucción
            mensajes_completos = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            completion = client.chat.completions.create(
                messages=mensajes_completos,
                model="llama-3.3-70b-versatile",
            )
            
            respuesta = completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error de sistema: {e}")
