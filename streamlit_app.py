import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. ESTÉTICA PREMIUM CON FLECHA BLINDADA ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE BLINDADA (BUSCA MÚLTIPLES SELECTORES) */
    [data-testid="stSidebarCollapsedControl"], 
    .st-emotion-cache-6q9sum, 
    button[kind="headerNoContext"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0px 10px 10px 0px !important;
        left: 0px !important;
        top: 15px !important;
        width: 50px !important;
        height: 40px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 999999 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Asegurar que el icono dentro sea blanco */
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
    }

    /* Ocultar el Header pero dejar espacio para la flecha */
    [data-testid="stHeader"] { 
        background: transparent !important; 
        color: transparent !important;
    }
    
    footer { visibility: hidden; }

    /* Neón Rojo Roto */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN ---
ESPECIALIDADES = {
    "Abogada": "como Abogada Senior.", "Amazon Pro": "como Especialista en Amazon.",
    "Marketing": "como Directora de Marketing.", "Estratega": "como CEO Advisor.",
    "Médico": "como Médico Especialista.", "Finanzas": "como Analista de Inversiones.",
    "IA Pro": "como Arquitecto de IA.", "Seguridad": "como Experto en Ciberseguridad."
}

TONOS = {
    "Analítica": "Tono lógico.", "Sarcástica": "Tono cínico.", "Empática": "Tono suave.",
    "Motivadora": "Tono enérgico.", "Ejecutiva": "Tono sobrio.", "Conspiranoica": "Tono suspicaz."
}

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def guardar_nube(mensajes):
    if mensajes:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
        except: pass

if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. PANEL LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    st.divider()
    especialidad = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    personalidad = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    st.divider()
    if st.button("RECOMENDAR LITERATURA"):
        try:
            instruccion = f"Actúa {ESPECIALIDADES[especialidad]} con {TONOS[personalidad]}. Recomienda 3 libros de tu área ({especialidad})."
            c = client.chat.completions.create(messages=[{"role":"system","content": instruccion}], model="llama-3.1-8b-instant")
            respuesta = c.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            st.rerun()
        except: st.warning("Servidor ocupado.")
    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            m_u = chat['messages'][0]['content'][:20].upper()+"..." if chat['messages'] else "VACÍO"
            if st.button(f"{m_u}", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 4. CUERPO PRINCIPAL ---
def enviar_c(t):
    sys_inst = f"Identidad TOTAL: {ESPECIALIDADES[especialidad]} Tono ABSOLUTO: {TONOS[personalidad]}."
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(messages=[{"role":"system","content": sys_inst}] + st.session_state.messages[-10:], model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_c(f"Análisis como {labels[i]}"); st.rerun()

st.divider()

for msg in st.session_state.messages:
    if "Identidad TOTAL" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {especialidad}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content": f"Eres RUTH {ESPECIALIDADES[especialidad]} {TONOS[personalidad]}"}] + st.session_state.messages[-10:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
