import streamlit as st
from groq import Groq
from supabase import create_client, Client
from PyPDF2 import PdfReader
import os
import datetime
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA (CSS BLINDADO) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* FONDO Y PARTÍCULAS */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(circle at 50% 50%, rgba(255, 75, 75, 0.02) 0%, transparent 80%),
                          radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 100% 100%, 30px 30px !important;
    }

    /* FLECHA DE RESCATE (REFORZADA) */
    button[kind="headerNoContext"], [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0 10px 10px 0 !important;
        left: 0 !important;
        top: 20px !important;
        width: 60px !important;
        height: 50px !important;
        display: flex !important;
        z-index: 9999999 !important;
        box-shadow: 5px 0 15px rgba(255, 75, 75, 0.4) !important;
    }
    
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }

    /* TÍTULO NEÓN */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* LOGIN FORM */
    .login-box {
        max-width: 400px; margin: 100px auto; padding: 2rem;
        background: rgba(26, 29, 36, 0.8); border: 1px solid #ff4b4b;
        border-radius: 15px; text-align: center;
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.2);
    }

    /* BOTONES GHOST */
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE LOGIN LOCAL ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">SYSTEM ACCESS</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        user = st.text_input("USUARIO", placeholder="Introduce tu usuario...")
        passw = st.text_input("CONTRASEÑA", type="password", placeholder="••••••••")
        
        if st.button("INICIAR SESIÓN"):
            # AQUÍ PUEDES CAMBIAR TU USUARIO Y CONTRASEÑA
            if user == "admin" and passw == "ruth2026":
                st.session_state.logged_in = True
                st.success("Acceso concedido.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- 3. CONEXIONES (SÓLO SI ESTÁ LOGUEADO) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
ruth_avatar = "logo_ruth.png" if os.path.exists("logo_ruth.png") else "●"

def guardar_nube(mensajes):
    if len(mensajes) > 1:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
        except: pass

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    if st.button("NUEVA CONVERSACIÓN"):
        guardar_nube(st.session_state.get('messages', []))
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    ESPECIALIDADES = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA.", "Seguridad": "Seguridad."}
    TONOS = {"Analítica": "Lógica.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}
    
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            tit = "VACÍO"
            for m in chat['messages']:
                if m['role'] == 'user': tit = m['content'][:15].upper() + "..."; break
            if st.button(f"{tit}", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: st.caption("Historial en espera")

# --- 5. INTERFAZ PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []

# Botones Ghost
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Acción: {labels[i]}"})
            sys_i = f"Eres RUTH {ESPECIALIDADES[esp_act]} ({TONOS[ton_act]})."
            c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:])
            st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content}); st.rerun()

st.divider()

for msg in st.session_state.messages:
    if "Acción:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        sys_i = f"Identidad: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}. Dinamismo total."
        c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:])
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
