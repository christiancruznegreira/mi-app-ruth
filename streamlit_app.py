import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA FIJA ---
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

    /* BARRA LATERAL FIJA: Ocultar flecha de colapsar y Header superior */
    [data-testid="stSidebarCollapsedControl"], [data-testid="stHeader"] {
        display: none !important;
    }

    /* Ajuste de espaciado tras quitar el header */
    .main .block-container {
        padding-top: 2rem !important;
    }

    /* EFECTO NEÓN ROJO ROTO */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00, 0 0 80px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { 
        text-align: center; color: #ff4b4b; font-size: 6rem; 
        animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.5rem; 
    }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -15px; margin-bottom: 2rem;}

    /* Botones con Brillo */
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

    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIÓN (GROQ Y SUPABASE) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Error técnico en Secrets. Revisa tus llaves API.")
    st.stop()

# --- 3. DICCIONARIO DE EXPERTOS ---
EXPERTOS = {
    "Abogada": "Eres RUTH Abogada Senior. Rigor legal, tono formal y sin disculpas.",
    "Amazon Pro": "Eres RUTH Especialista Amazon FBA. SEO y ventas. Directa.",
    "Marketing": "Eres RUTH Directora Marketing. Persuasiva y creativa.",
    "Estratega": "Eres RUTH CEO Advisor. Estrategia y escalabilidad."
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

# --- 5. PANEL LATERAL FIJO (CENTRO DE MANDO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; margin-top: -20px;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Especialidad de RUTH:", list(EXPERTOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.8rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        fecha = chat['created_at'][11:16]
        if st.button(f"📜 Chat {fecha}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 6. PROCESAMIENTO Y CUERPO ---
def enviar_p(t):
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(
        messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages,
        model="llama-3.3-70b-versatile"
    )
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

# Botones rápidos superiores
col1, col2, col3, col4 = st.columns(4)
with col1: 
    if st.button("📝 Email"): enviar_p(f"Redacta un correo profesional como {modo}."); st.rerun()
with col2: 
    if st.button("⚖️ Análisis"): enviar_p(f"Análisis experto como {modo}."); st.rerun()
with col3: 
    if st.button("📦 Amazon"): enviar_p(f"Optimización SEO como Amazon Pro."); st.rerun()
with col4: 
    if st.button("💡 Estrategia"): enviar_p(f"Estrategia disruptiva como {modo}."); st.rerun()

st.divider()

# --- 7. MOSTRAR CHAT ---
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

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
