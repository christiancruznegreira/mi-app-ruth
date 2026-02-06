import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (MINIMALISTA) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; opacity: 1; }
        50% { color: #660000; text-shadow: none; opacity: 0.8; }
    }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    /* REJILLA PARA 8 BOTONES */
    [data-testid="column"] { padding: 0px 1px !important; text-align: center !important; }
    .stButton>button {
        border: none !important;
        background-color: transparent !important;
        color: #aaaaaa !important; 
        width: 100% !important;
        height: 40px !important;
        transition: 0.2s ease;
        text-transform: uppercase;
        font-size: 0.48rem !important; 
        font-weight: 400 !important;
        letter-spacing: 0.01rem !important;
        white-space: nowrap !important;
        cursor: pointer;
    }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; background-color: transparent !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. PERSONALIDADES PROFESIONALES 2026 ---
PERSONALIDADES = {
    "Abogada": "Eres RUTH Legal Advisor. Tono formal, jurídico y técnico.",
    "Amazon Pro": "Eres RUTH Amazon Strategist. SEO, ventas y rentabilidad.",
    "Marketing": "Eres RUTH Copywriter. Persuasiva y creativa.",
    "Estratega": "Eres RUTH CEO Advisor. Escalabilidad y visión ejecutiva.",
    "Médico": "Eres RUTH Médico. Científica y empática.",
    "Finanzas": "Eres RUTH Wealth Manager. Experta en inversiones, análisis de mercado y gestión de riesgos financieros.",
    "IA Pro": "Eres RUTH AI Architect. Experta en automatización, prompts y sistemas de inteligencia artificial avanzada.",
    "Seguridad": "Eres RUTH Cybersecurity Lead. Experta en protección de datos, auditoría de seguridad y privacidad digital."
}

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. LOGICA DE COMANDOS ---
def enviar_c(etiqueta, modo_actual):
    prompts_base = {
        "LEGAL": f"Analiza este caso jurídico como experta en leyes: ",
        "AMAZON": f"Optimiza el SEO y ventas de este producto en Amazon: ",
        "MARKETING": f"Crea una campaña persuasiva y creativa para: ",
        "ESTRATEGIA": f"Define una estrategia CEO para escalar este negocio: ",
        "SALUD": f"Explica este concepto médico con rigor científico: ",
        "FINANZAS": f"Analiza esta oportunidad de inversión o activo financiero: ",
        "IA PRO": f"Diseña una automatización o prompt avanzado para: ",
        "SEGURIDAD": f"Realiza una auditoría de seguridad o privacidad sobre: "
    }
    orden = prompts_base.get(etiqueta, "Hola, asísteme profesionalmente.")
    st.session_state.messages.append({"role": "user", "content": orden})
    c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo_actual]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    modo = st.selectbox("Especialidad Activa:", list(PERSONALIDADES.keys()))
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
                st.session_state.messages = chat['messages']
                st.rerun()
    except: pass

# --- 6. CUERPO (8 BOTONES GHOST) ---
cols = st.columns(8)
labels = ["LEGAL", "AMAZON", "MARKETING", "ESTRATEGIA", "SALUD", "FINANZAS", "IA PRO", "SEGURIDAD"]

for i in range(8):
    with cols[i]:
        if st.button(labels[i]): 
            enviar_c(labels[i], modo)
            st.rerun()

st.divider()

# --- 7. CHAT ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
