import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time

# --- 1. ESTÉTICA iOS 26 CRYSTAL (CSS REFORZADO) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* FONDO BASE Y PARTÍCULAS */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 75, 75, 0.08) 0%, transparent 25%),
            radial-gradient(circle at 80% 70%, rgba(255, 75, 75, 0.08) 0%, transparent 25%),
            radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 30px 30px !important;
        animation: drift 20s infinite alternate ease-in-out;
    }
    @keyframes drift { from { background-position: 0% 0%; } to { background-position: 5% 5%; } }

    /* EFECTO CRISTAL EN BARRA LATERAL (SELECTORES ESPECÍFICOS) */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 18, 22, 0.5) !important;
        backdrop-filter: blur(25px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(150%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stSidebarContent { background: transparent !important; }

    /* MENSAJES DE CHAT TIPO CRISTAL iOS */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 15px !important;
    }

    /* FLECHA DE RESCATE ROJA GIGANTE */
    button[kind="headerNoContext"], [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0 15px 15px 0 !important;
        left: 0 !important; top: 20px !important;
        width: 70px !important; height: 55px !important;
        display: flex !important; align-items: center !important; 
        justify-content: center !important; z-index: 9999999 !important;
        box-shadow: 5px 0 25px rgba(255, 0, 0, 0.5) !important;
    }

    /* TÍTULO NEÓN */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 4rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.7rem; letter-spacing: 0.4rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* BOTONES GHOST */
    .stButton>button { 
        border: none !important; background-color: transparent !important; color: #999 !important; 
        width: 100% !important; transition: 0.3s; text-transform: uppercase; font-size: 0.55rem !important; 
        letter-spacing: 0.1rem;
    }
    .stButton>button:hover { color: #ff4b4b !important; text-shadow: 0 0 10px #f00; transform: scale(1.05); }

    /* INPUTS LOGIN CRYSTAL */
    div[data-testid="stTextInput"] label { color: #ff4b4b !important; font-size: 0.6rem !important; letter-spacing: 0.1rem; }
    div[data-testid="stTextInput"] input { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 15px !important; text-align: center;
    }
    
    header, footer { visibility: hidden; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
ruth_avatar = "logo_ruth.png" if os.path.exists("logo_ruth.png") else "●"

# --- 3. GESTIÓN DE ACCESO ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"

def login_ui():
    st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        if st.session_state.auth_mode == "login":
            st.markdown("<h4 style='color:white; text-align:center;'>ENTRAR</h4>", unsafe_allow_html=True)
            u = st.text_input("USUARIO", key="l_u")
            p = st.text_input("CONTRASEÑA", type="password", key="l_p")
            if st.button("ACCEDER AL SISTEMA"):
                res = supabase.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.logged_in = True; st.session_state.user_name = u; st.rerun()
                else: st.error("Acceso denegado.")
            if st.button("¿ERES NUEVO? CREAR CUENTA"):
                st.session_state.auth_mode = "signup"; st.rerun()
        else:
            st.markdown("<h4 style='color:white; text-align:center;'>REGISTRO</h4>", unsafe_allow_html=True)
            nu = st.text_input("NUEVO USUARIO", key="s_u")
            np = st.text_input("NUEVA CONTRASEÑA", type="password", key="s_p")
            if st.button("REGISTRAR SOCIO"):
                try:
                    supabase.table("usuarios").insert({"username": nu, "password": np}).execute()
                    st.success("Cuenta creada."); time.sleep(1.2); st.session_state.auth_mode = "login"; st.rerun()
                except: st.error("Ese usuario ya existe.")
            if st.button("VOLVER AL LOGIN"):
                st.session_state.auth_mode = "login"; st.rerun()

if not st.session_state.logged_in:
    login_ui(); st.stop()

# --- 4. BARRA LATERAL (WORKSPACE CRYSTAL) ---
with st.sidebar:
    st.markdown(f"<h2 style='color: #ff4b4b; font-weight: 100; letter-spacing: 0.3rem;'>{st.session_state.user_name.upper()}</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []; st.rerun()
    if st.button("SALIR DEL SISTEMA"):
        st.session_state.logged_in = False; st.rerun()
    
    st.divider()
    # DICCIONARIOS CORREGIDOS
    ESPECIALIDADES = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO Advisor.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA Pro.", "Seguridad": "Seguridad."}
    TONOS = {"Analítica": "Fría.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}
    
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem; letter-spacing: 0.1rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"📜 {tit}..."): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
if "messages" not in st.session_state: st.session_state.messages = []

# Botones Ghost Superiores (8 Especialidades)
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Acción: {labels[i]}"})
            sys_i = f"Eres RUTH {ESPECIALIDADES[esp_act]} ({TONOS[ton_act]}). Responde ahora."
            c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:])
            st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
            try: supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
            except: pass
            st.rerun()

st.divider()
for msg in st.session_state.messages:
    if "Acción:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        sys_i = f"Identidad RUTH: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}."
        c = client.chat.completions.create(messages=[{"role":"system","content": sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
        try: supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
        except: pass
