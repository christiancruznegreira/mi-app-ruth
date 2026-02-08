import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time

# --- 1. ESTÉTICA iOS 26 GLASS (CSS AVANZADO) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* FONDO BASE CON PARTÍCULAS */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 75, 75, 0.07) 0%, transparent 25%),
            radial-gradient(circle at 80% 70%, rgba(255, 75, 75, 0.07) 0%, transparent 25%),
            radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 30px 30px !important;
        animation: drift 20s infinite alternate ease-in-out;
    }
    @keyframes drift { from { background-position: 0% 0%; } to { background-position: 5% 5%; } }

    /* EFECTO CRISTAL EN BARRA LATERAL */
    [data-testid="stSidebar"] > div:first-child {
        background-color: rgba(20, 23, 28, 0.7) !important;
        backdrop-filter: blur(15px) saturate(150%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* MENSAJES DE CHAT TIPO CRISTAL */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    /* FLECHA DE RESCATE ROJA (GRANDE PARA MÓVIL) */
    button[kind="headerNoContext"], [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0 15px 15px 0 !important;
        left: 0 !important; top: 15px !important;
        width: 70px !important; height: 60px !important;
        display: flex !important; z-index: 9999999 !important;
        box-shadow: 5px 0 25px rgba(255, 0, 0, 0.5) !important;
    }
    
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }

    /* TÍTULO NEÓN */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 4rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1rem; }
    .ruth-subtitle { text-align: center; color: #666; font-size: 0.7rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem; font-weight: bold;}

    /* BOTONES GHOST */
    .stButton>button { 
        border: none !important; background-color: transparent !important; color: #888 !important; 
        width: 100% !important; height: 45px !important; transition: 0.3s; 
        text-transform: uppercase; font-size: 0.5rem !important; white-space: nowrap !important;
    }
    .stButton>button:hover { color: #ff4b4b !important; text-shadow: 0 0 10px #f00; transform: translateY(-2px); }

    /* INPUTS LOGIN CRYSTAL */
    div[data-testid="stTextInput"] label { display: none; }
    div[data-testid="stTextInput"] input { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 12px !important; text-align: center;
    }
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
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.session_state.auth_mode == "login":
            u = st.text_input("U", placeholder="USUARIO", key="l_u")
            p = st.text_input("P", type="password", placeholder="CONTRASEÑA", key="l_p")
            if st.button("ACCEDER"):
                res = supabase.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.logged_in = True; st.session_state.user_name = u; st.rerun()
                else: st.error("Error de acceso.")
            if st.button("CREAR CUENTA NUEVA"):
                st.session_state.auth_mode = "signup"; st.rerun()
        else:
            nu = st.text_input("NU", placeholder="USUARIO NUEVO", key="s_u")
            np = st.text_input("NP", type="password", placeholder="CONTRASEÑA NUEVA", key="s_p")
            if st.button("REGISTRAR SOCIO"):
                try:
                    supabase.table("usuarios").insert({"username": nu, "password": np}).execute()
                    st.success("Socio registrado."); time.sleep(1); st.session_state.auth_mode = "login"; st.rerun()
                except: st.error("Usuario ocupado.")
            if st.button("VOLVER AL LOGIN"):
                st.session_state.auth_mode = "login"; st.rerun()

if not st.session_state.logged_in:
    login_ui(); st.stop()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"<h3 style='color: white; font-weight: 200;'>{st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []; st.rerun()
    if st.button("SALIR"):
        st.session_state.logged_in = False; st.rerun()
    
    st.divider()
    ESP = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO Advisor.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA.", "Seguridad": "Seguridad."}
    TON = {"Analítica": "Lógica.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}
    esp_act = st.selectbox("E:", list(ESP.keys()))
    ton_act = st.selectbox("T:", list(TON.keys()))
    
    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}"): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
if "messages" not in st.session_state: st.session_state.messages = []

# Botones Ghost
cols = st.columns(8); labels = list(ESP.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Acción: {labels[i]}"})
            sys_i = f"Eres RUTH {ESP[esp_act]} ({TON[ton_act]})."
            c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:])
            st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
            try: supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
            except: pass
            st.rerun()

st.divider()
for msg in st.session_state.messages:
    if "Acción:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        sys_i = f"Identidad RUTH: {ESP[esp_act]} Tono: {TON[ton_act]}."
        c = client.chat.completions.create(messages=[{"role":"system","content": sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
        try: supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
        except: pass
