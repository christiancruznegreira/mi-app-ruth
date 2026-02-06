import streamlit as st
import google.generativeai as genai
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

# --- 2. CONFIGURACIÓN DEL CEREBRO GOOGLE ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: Falta GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Definimos el modelo de Google
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="Eres RUTH, una asistente de inteligencia artificial profesional, sofisticada y de élite. Tu estilo es minimalista y directo. Hoy es 6 de febrero de 2026. Tienes acceso a información actualizada."
)

# --- 3. GESTIÓN DEL CHAT ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

with st.sidebar:
    st.markdown("### PANEL DE CONTROL")
    if st.button("🔄 REINICIAR RUTH"):
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
    st.divider()
    st.caption("Cerebro: Google Gemini 2.0 (Feb 2026)")

# Mostrar historial de conversación
for message in st.session_state.chat.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Entrada de chat
if prompt := st.chat_input("Consulta a RUTH Professional..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Enviamos el mensaje a Google y recibimos respuesta fluida
            response = st.session_state.chat.send_message(prompt, stream=True)
            full_res = ""
            placeholder = st.empty()
            
            for chunk in response:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
            
            placeholder.markdown(full_res)
        except Exception as e:
            st.error(f"Error de sistema: {e}")
