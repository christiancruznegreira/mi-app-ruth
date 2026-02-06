import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (BARRA LATERAL PROTEGIDA) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Unificado */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE: Pestaña roja arriba a la izquierda */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0px 10px 10px 0px;
        left: 0px;
        top: 15px;
        padding: 5px;
    }

    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }

    /* EFECTO NEÓN ROJO ROTO */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -15px; margin-bottom: 3rem; font-weight: bold;}
    
    /* BOTONES GHOST */
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
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; opacity: 1; }
        50% { color: #660000; text-shadow: none; opacity: 0.8; }
    }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; background-color: transparent !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIOS DE INTELIGENCIA CRUZADA ---
ESPECIALIDADES = {
    "Psicóloga": "como Psicóloga Clínica experta en análisis de patrones de conducta y datos reales.",
    "Abogada": "como experta en Derecho y Consultoría Legal.",
    "Amazon Pro": "como Especialista en Amazon FBA y algoritmos.",
    "Marketing": "como Directora de Marketing y Copywriter Pro.",
    "Estratega": "como CEO Advisor y Estratega de Negocios.",
    "Médico": "como Médico Especialista con rigor científico.",
    "Finanzas": "como Analista de Inversiones y Wealth Manager.",
    "IA Pro": "como Arquitecto de IA y experto en automatización.",
    "Seguridad": "como Líder en Ciberseguridad y Privacidad."
}

TONOS = {
    "Conspiranoica": "Tu tono es suspicaz, cuestionas todo y buscas 'la verdad oculta' detrás de cada dato. Crees que nada es casualidad y que hay estructuras de poder vigilando.",
    "Analítica": "Tu tono es basado en datos, frío, preciso y lógico.",
    "Motivadora": "Tu tono es inspirador, lleno de energía y optimismo.",
    "Sarcástica": "Tu tono es irónico, brillante pero mordaz.",
    "Ejecutiva": "Tu tono es de alto nivel CEO, breve y directo al grano.",
    "Empática": "Tu tono es suave, comprensivo y paciente."
}

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    especialidad = st.selectbox("Especialidad:", list(ESPECIALIDADES.keys()))
    personalidad = st.selectbox("Personalidad:", list(TONOS.keys()))
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            msg_t = "Sin contenido"
            for m in chat['messages']:
                if m['role']=='user': 
                    msg_t = m['content'][:20].upper() + "..."
                    break
            if st.button(f"{msg_t} ({chat['created_at'][11:16]})", key=chat['id']):
                st.session_state.messages = chat['messages']
                st.rerun()
    except: pass

# --- 5. LÓGICA DE PROCESAMIENTO ---
def enviar_c(etiqueta):
    system_inst = f"Eres RUTH. Actúas {ESPECIALIDADES[especialidad]} {TONOS[personalidad]}"
    st.session_state.messages.append({"role": "user", "content": f"Ejecuta: {etiqueta}"})
    c = client.chat.completions.create(messages=[{"role":"system","content": system_inst}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8)
labels = ["LEGAL", "AMAZON", "MARKETING", "ESTRATEGIA", "SALUD", "FINANZAS", "IA PRO", "SEGURIDAD"]
for i in range(8):
    with cols[i]:
        if st.button(labels[i]): enviar_c(labels[i]); st.rerun()

st.divider()

for msg in st.session_state.messages:
    if "Eres RUTH" not in msg["content"] and "Ejecuta:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {especialidad} ({personalidad})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        system_inst = f"Eres RUTH. Tu rol es actuar {ESPECIALIDADES[especialidad]} {TONOS[personalidad]}"
        c = client.chat.completions.create(messages=[{"role":"system","content": system_inst}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
