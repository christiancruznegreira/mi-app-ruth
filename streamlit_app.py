import streamlit as st
from groq import Groq
import os
import datetime

# --- 1. CONFIGURACIÓN VISUAL (BARRA LATERAL SIEMPRE EXPANDIDA) ---
st.set_page_config(
    page_title="RUTH Ultra", 
    page_icon="●", 
    layout="wide",
    initial_sidebar_state="expanded" # Esto obliga a que la barra salga sí o sí
)

st.markdown("""
    <style>
    /* Fondo con Patrón Unificado */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* Título RUTH */
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0; text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4);}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}

    /* Botones con Glow Rojo */
    .stButton>button {
        border-radius: 15px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important;
    }

    /* Color de texto claro */
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    
    /* Asegurar que el botón de cerrar la barra sea visible */
    [data-testid="stSidebarNav"] { color: white !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">ULTRA PROFESSIONAL SUITE</div>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE MEMORIA ---
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = {}

def procesar_prompt(texto, modo_ia):
    st.session_state.messages.append({"role": "user", "content": texto})
    client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    try:
        c = client.chat.completions.create(
            messages=[{"role":"system","content":f"Eres RUTH {modo_ia}"}]+st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
    except Exception as e:
        st.error(f"Error: {e}")

# --- 3. BARRA LATERAL (CENTRO DE MANDO SIEMPRE ABIERTO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            h = datetime.datetime.now().strftime("%H:%M")
            st.session_state.history[f"Chat {h}"] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Identidad de RUTH:", ["Abogada", "Amazon Pro", "Marketing", "Estratega"])
    
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL</p>", unsafe_allow_html=True)
    for chat_id in st.session_state.history:
        if st.button(f"📜 {chat_id}"):
            st.session_state.messages = st.session_state.history[chat_id]
            st.rerun()

# --- 4. INTERFAZ PRINCIPAL ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📝 Email"): procesar_prompt("Redacta un email profesional.", modo); st.rerun()
with col2:
    if st.button("⚖️ Legal"): procesar_prompt("Revisa esta cláusula legal.", modo); st.rerun()
with col3:
    if st.button("📦 Amazon"): procesar_prompt("Optimiza SEO Amazon.", modo); st.rerun()
with col4:
    if st.button("💡 Estrategia"): procesar_prompt("Propón una estrategia.", modo); st.rerun()

st.divider()

# --- 5. MOSTRAR CHAT ---
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Hablando con RUTH {modo}..."):
    procesar_prompt(prompt, modo)
    st.rerun()
