import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN VISUAL PREMIUM Y TÍTULO NEÓN ROJO ---
st.set_page_config(
    page_title="RUTH Professional", 
    page_icon="●", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Fondo con Patrón Unificado */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }

    /* EFECTO NEÓN ROJO ROTO */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 
                0 0 4px #ff0000,
                0 0 11px #ff0000,
                0 0 19px #ff0000,
                0 0 40px #ff4b4b,
                0 0 80px #ff4b4b,
                0 0 90px #ff4b4b,
                0 0 100px #ff4b4b;
            color: #ff4b4b;
        }
        20%, 24%, 55% {        
            text-shadow: none;
            color: #330000; 
        }
    }

    .ruth-header {
        text-align: center;
        padding-top: 2rem;
        letter-spacing: 1.5rem;
        font-weight: 100;
        color: #ff4b4b;
        font-size: 6rem; 
        animation: flicker 3s infinite alternate;
        margin-bottom: 0px;
    }
    
    .ruth-subtitle {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        letter-spacing: 0.4rem;
        margin-top: -15px;
        margin-bottom: 3rem;
    }

    /* Botones con Brillo */
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

# --- 3. EXPERTOS ---
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: white; font-weight: 200;'>WORKSPACE</h3>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    st.divider()
    modo = st.selectbox("Identidad de RUTH:", list(EXPERTOS.keys()))
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        fecha = chat['created_at'][11:16]
        if st.button(f"📜 Chat {fecha}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 6. PROCESAMIENTO ---
def procesar_prompt(texto, modo_ia):
    st.session_state.messages.append({"role": "user", "content": texto})
    instruccion = EXPERTOS[modo_ia]
    try:
        c = client.chat.completions.create(
            messages=[{"role":"system","content": instruccion}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
    except Exception as e:
        st.error(f"Error: {e}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📝 Email"): procesar_prompt(f"Como {modo}, redacta un correo profesional...", modo); st.rerun()
with col2:
    if st.button("⚖️ Análisis"): procesar_prompt(f"Haz un análisis experto sobre...", modo); st.rerun()
with col3:
    if st.button("📦 Optimización"): procesar_prompt(f"Como experta en Amazon, optimiza...", modo); st.rerun()
with col4:
    if st.button("💡 Estrategia"): procesar_prompt(f"Propón una idea de negocio desde tu visión de {modo}...", modo); st.rerun()

st.divider()

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
