import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA DINÁMICA ---
st.set_page_config(
    page_title="RUTH Pro", 
    page_icon="●", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Empieza cerrada para lucir la flecha
)

st.markdown("""
    <style>
    /* Fondo con Patrón Unificado para todo */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* ANIMACIÓN DE LA FLECHA ROJA PARPADEANTE */
    @keyframes arrow-flicker {
        0%, 100% { opacity: 1; transform: scale(1.1); filter: drop-shadow(0 0 10px #ff0000); }
        50% { opacity: 0.3; transform: scale(1); filter: none; }
    }

    /* Estilo para la Flecha de Streamlit (Botón de Expandir) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        top: 20px;
        left: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: arrow-flicker 2s infinite ease-in-out;
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.5);
    }
    
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        width: 30px;
        height: 30px;
    }

    header, footer { visibility: hidden; }

    /* Neón Rojo Roto para el Título */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 6rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.5rem; padding-top: 2rem;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -15px; margin-bottom: 3rem;}

    /* Botones con Glow */
    .stButton>button {
        border-radius: 12px !important;
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
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# --- 3. EXPERTOS ---
EXPERTOS = {
    "Abogada": "Eres RUTH Abogada Senior de Élite.",
    "Amazon Pro": "Eres RUTH Especialista en Amazon.",
    "Marketing": "Eres RUTH Directora de Marketing.",
    "Estratega": "Eres RUTH CEO Advisor."
}

# --- 4. FUNCIONES DE NUBE ---
def guardar_nube(mensajes):
    try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
    except: pass

def cargar_nube():
    try: 
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        return res.data
    except: return []

if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. PANEL LATERAL (SIDEBAR DINÁMICO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Especialidad:", list(EXPERTOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 6. PROCESAMIENTO Y CHAT ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
