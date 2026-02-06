import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (FLECHA ROJA FIJA) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium Unificado */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE (GARANTIZADA Y ROJA) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0px 10px 10px 0px !important;
        left: 0px !important;
        top: 20px !important;
        width: 50px !important;
        height: 40px !important;
        display: flex !important;
        justify-content: center !important;
        z-index: 999999 !important;
        box-shadow: 5px 0px 15px rgba(255, 75, 75, 0.3) !important;
    }
    
    /* Asegurar que la flecha dentro del botón sea blanca */
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
    }

    /* Ocultar el Header pero dejar espacio para la flecha */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }

    /* Título Neón Rojo Roto */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; margin-bottom: 0px;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* BOTONES GHOST MINIMALISTAS */
    [data-testid="column"] { padding: 0 1px !important; }
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIOS Y CONEXIONES ---
ESPECIALIDADES = {"Abogada": "como Abogada Senior.", "Amazon Pro": "como Especialista en Amazon.", "Marketing": "como Directora Marketing.", "Estratega": "como CEO Advisor.", "Médico": "como Médico.", "Finanzas": "como Analista Finanzas.", "IA Pro": "como Arquitecto IA.", "Seguridad": "como Experto Seguridad."}
TONOS = {"Sarcástica": "Tono cínico e irónico.", "Empática": "Tono suave y cálido.", "Analítica": "Tono lógico y frío.", "Motivadora": "Tono enérgico e inspirador.", "Ejecutiva": "Tono sobrio y directo.", "Conspiranoica": "Tono suspicaz."}

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            try: supabase.table("chats").insert({"user_email": "Invitado", "messages": st.session_state.messages}).execute()
            except: pass
        st.session_state.messages = []; st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>BIBLIOTECA</p>", unsafe_allow_html=True)
    if st.button("RECOMENDAR LITERATURA"):
        sys_l = f"Ignora el pasado. Eres RUTH {ESPECIALIDADES[esp_act]} con {TONOS[ton_act]}. Recomienda 3 libros de tu área."
        c_l = client.chat.completions.create(messages=[{"role":"system","content":sys_l}], model="llama-3.1-8b-instant")
        st.session_state.messages.append({"role": "assistant", "content": c_l.choices[0].message.content})
        st.rerun()

    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}..."): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 4. CUERPO Y CHAT ---
def enviar_c(t):
    sys_i = f"Identidad TOTAL: {ESPECIALIDADES[esp_act]} Tono ABSOLUTO: {TONOS[ton_act]}. Responde ahora."
    st.session_state.messages.append({"role": "user", "content": f"Acción: {t}"})
    c = client.chat.completions.create(messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_c(labels[i]); st.rerun()

st.divider()

for msg in st.session_state.messages:
    if "Acción:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

if prompt := st.chat_input(f"Hablando con RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        sys_i = f"Identidad RUTH: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}. Dinamismo total."
        c = client.chat.completions.create(messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
