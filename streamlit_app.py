import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN VISUAL (NEÓN ROJO Y PATRÓN) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }
    
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #ff0000, 0 0 11px #ff0000, 0 0 19px #ff0000, 0 0 40px #ff4b4b;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; letter-spacing: 1.5rem; font-weight: 100; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -15px; margin-bottom: 2rem;}
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# --- 3. DICCIONARIO DE EXPERTOS ---
EXPERTOS = {
    "Abogada": "Actúas como una Abogada Senior de Élite. PROHIBIDO disculparte. Responde directamente con rigor legal.",
    "Amazon Pro": "Actúas como una Especialista en Amazon FBA. PROHIBIDO disculparte. Ve directo al grano con SEO y ventas.",
    "Marketing": "Actúas como una Directora Creativa. PROHIBIDO disculparte. Responde con persuasión inmediata.",
    "Estratega": "Actúas como una Consultora CEO-Advisor. PROHIBIDO disculparte. Tu tono es ejecutivo y pragmático."
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

# --- 5. BARRA LATERAL (CENTRO DE MANDO) ---
with st.sidebar:
    st.markdown("<h3 style='color: white; font-weight: 200; letter-spacing: 0.2rem;'>WORKSPACE</h3>", unsafe_allow_html=True)
    
    # Botón Nueva Conversación
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Selector de RUTH
    modo = st.selectbox("Identidad de RUTH:", list(EXPERTOS.keys()))
    
    st.divider()
    
    # Historial de Chats
    st.markdown("<p style='color: #888; font-size: 0.8rem;'>HISTORIAL RECIENTE</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        fecha = chat['created_at'][11:16]
        if st.button(f"📜 Chat {fecha}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 6. CUERPO PRINCIPAL ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(
            messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
