import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA PREMIUM ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo con Patrón */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }

    /* Neón Rojo Roto para el Título */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00, 0 0 80px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5.5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.5rem; margin-bottom: 0px;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem;}

    /* BOTONES CON ICONOS ROJOS Y GLOW */
    .stButton>button {
        border-radius: 12px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        height: 80px !important; /* Más altos para que luzca el icono */
        transition: 0.3s;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem !important;
    }
    .stButton>button:hover {
        background-color: rgba(255, 75, 75, 0.2) !important;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important;
        transform: translateY(-3px);
    }

    /* Estilo del texto en los botones */
    .stButton>button div p {
        color: #ff4b4b !important;
        font-weight: bold !important;
        margin-top: 5px;
    }

    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES Y LOGICA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

PERSONALIDADES = {"Abogada": "RUTH Legal.", "Amazon Pro": "RUTH Amazon.", "Marketing": "RUTH Marketing.", "Estratega": "RUTH CEO.", "Médico": "RUTH Médica.", "Anime": "RUTH Anime."}

if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    modo = st.selectbox("Especialidad Activa:", list(PERSONALIDADES.keys()))

# --- 4. CUERPO PRINCIPAL (BOTONES CON ICONOS ROJOS) ---
def enviar_c(t):
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

# Definimos iconos rojos elegantes usando texto y emojis estilizados
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1: 
    if st.button("📧\nEmail"): enviar_c("Redacta un correo."); st.rerun()
with col2: 
    if st.button("⚖️\nLegal"): enviar_c("Análisis experto."); st.rerun()
with col3: 
    if st.button("📦\nAmazon"): enviar_c("Optimiza SEO Amazon."); st.rerun()
with col4: 
    if st.button("🚀\nEstrategia"): enviar_c("Idea disruptiva."); st.rerun()
with col5: 
    if st.button("💊\nSalud"): enviar_c("Consulta médica."); st.rerun()
with col6: 
    if st.button("🔥\nAnime"): enviar_c("Recomendación anime."); st.rerun()

st.divider()

# --- 5. MOSTRAR CHAT ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Hablando con RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
