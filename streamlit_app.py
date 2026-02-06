import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. ESTÉTICA PREMIUM (SIN TOCAR) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00, 0 0 80px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5.5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.5rem; margin-bottom: 0px;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem;}
    .stButton>button { border-radius: 12px !important; border: 1px solid #ff4b4b !important; background-color: rgba(255, 75, 75, 0.05) !important; color: white !important; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #ff4b4b !important; box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIO DE PERSONALIDADES RADICALES ---
PERSONALIDADES = {
    "Abogada": (
        "Eres RUTH Legal Advisor. Tu tono es frío, formal y extremadamente técnico. "
        "Utilizas jerga jurídica, analizas riesgos y exiges precisión. No usas emojis. "
        "PROHIBIDO disculparte por cambiar de modo. Eres una experta senior en leyes."
    ),
    "Amazon Pro": (
        "Eres RUTH Amazon Strategist. Tu enfoque es puramente comercial y agresivo. "
        "Hablas de algoritmos, conversiones (CTR), optimización de keywords y rentabilidad. "
        "Tu meta es que el usuario venda más. Sé directa y pragmática."
    ),
    "Marketing": (
        "Eres RUTH Creative Copywriter. Tu tono es magnético, persuasivo y vibrante. "
        "Utilizas psicología del consumidor y gatillos mentales. Creas deseo en cada frase. "
        "Eres experta en storytelling y ventas emocionales."
    ),
    "Estratega": (
        "Eres RUTH CEO Consultant. Tu visión es a 30,000 pies de altura. "
        "Analizas escalabilidad, flujos de caja y ventaja competitiva. Hablas como una jefa de nivel ejecutivo. "
        "Tu lenguaje es sobrio, visionario y orientado a grandes resultados."
    )
}

# --- 3. CONEXIONES ---
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def guardar_nube(mensajes):
    if mensajes:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
    except: pass

def cargar_nube():
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        return res.data
    except: return []

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. PANEL LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    st.divider()
    
    # Selector de Personalidad
    modo = st.selectbox("Identidad Activa:", list(PERSONALIDADES.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 5. CUERPO PRINCIPAL ---
def enviar_comando(t):
    st.session_state.messages.append({"role": "user", "content": t})
    instruccion = PERSONALIDADES[modo]
    c = client.chat.completions.create(
        messages=[{"role":"system","content": instruccion}] + st.session_state.messages,
        model="llama-3.3-70b-versatile"
    )
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

col1, col2, col3, col4 = st.columns(4)
with col1: 
    if st.button("📝 Email"): enviar_comando("Redacta un correo profesional impecable."); st.rerun()
with col2: 
    if st.button("⚖️ Análisis"): enviar_comando("Realiza un análisis profesional profundo."); st.rerun()
with col3: 
    if st.button("📦 Amazon"): enviar_comando("Optimiza el SEO para un listado de Amazon."); st.rerun()
with col4: 
    if st.button("💡 Estrategia"): enviar_comando("Propón una idea de negocio disruptiva."); st.rerun()

st.divider()

# Mostrar Chat con Logo Fijo
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Hablando con RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(
            messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
