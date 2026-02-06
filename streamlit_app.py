import streamlit as st
from groq import Groq
import os
import datetime
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN Y ESTÉTICA PREMIUM (SIDEBAR INCLUIDO)
st.set_page_config(page_title="RUTH Ultra", page_icon="●", layout="wide")

st.markdown("""
    <style>
    /* Fondo con Patrón Unificado (Principal y Sidebar) */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* Flecha de desplegar Sidebar (Roja y Blanca) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 50%;
    }

    /* Ocultar elementos innecesarios */
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden !important; }

    /* Branding RUTH */
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0; text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4);}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}

    /* Botones con Brillo Rojo (Glow) */
    .stButton>button {
        border-radius: 15px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        transition: 0.3s;
        letter-spacing: 0.1rem;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important;
        color: white !important;
    }

    /* Estilo del Chat */
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">ULTRA PROFESSIONAL SUITE</div>
""", unsafe_allow_html=True)

# 2. GESTIÓN DE MEMORIA E HISTORIAL
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = {}

def procesar_prompt(texto_usuario, modo_actual):
    st.session_state.messages.append({"role": "user", "content": texto_usuario})
    client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    
    # Personalidad dinámica según el modo
    sys_msg = f"Eres RUTH en modo {modo_actual}. Eres una IA profesional de élite. Responde con elegancia y precisión."
    
    full_msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
    try:
        completion = client.chat.completions.create(
            messages=full_msgs,
            model="llama-3.3-70b-versatile"
        )
        respuesta = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
    except Exception as e:
        st.error(f"Error: {e}")

# 3. PANEL LATERAL (SIDEBAR)
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    # Botón Nueva Conversación
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            hora = datetime.datetime.now().strftime("%H:%M")
            st.session_state.history[f"Chat {hora}"] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Selector de RUTH
    modo = st.selectbox(
        "Identidad de RUTH:",
        ["Abogada & Legal", "Amazon FBA Experta", "Copywriter Creativa", "Estratega CEO"]
    )
    
    st.divider()
    
    # Historial de Chats
    st.markdown("<p style='color: #888; font-size: 0.8rem;'>HISTORIAL RECIENTE</p>", unsafe_allow_html=True)
    for chat_id in reversed(list(st.session_state.history.keys())):
        if st.button(f"📜 {chat_id}"):
            st.session_state.messages = st.session_state.history[chat_id]
            st.rerun()
            
    st.divider()
    uploaded_file = st.file_uploader("📄 Analizador de PDF", type="pdf")

# 4. BOTONES DE ACCIÓN RÁPIDA (INTERFAZ PRINCIPAL)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📝 Redactar Email"):
        procesar_prompt("RUTH, redacta un email profesional elegante para un cliente.", modo)
        st.rerun()
with col2:
    if st.button("⚖️ Revisar Cláusula"):
        procesar_prompt("RUTH, analiza si esta cláusula legal es segura y profesional.", modo)
        st.rerun()
with col3:
    if st.button("📦 SEO Amazon"):
        procesar_prompt("RUTH, optimiza el SEO de este producto para Amazon.", modo)
        st.rerun()
with col4:
    if st.button("💡 Nueva Estrategia"):
        procesar_prompt("RUTH, propón una estrategia de negocio disruptiva.", modo)
        st.rerun()

st.divider()

# 5. MOSTRAR CHAT
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# Entrada de texto manual
if prompt := st.chat_input(f"Hablando con RUTH {modo}..."):
    procesar_prompt(prompt, modo)
    st.rerun()
