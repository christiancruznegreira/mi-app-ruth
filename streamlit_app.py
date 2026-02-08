import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time

# --- 1. ESTÉTICA iOS 26 CRYSTAL (CSS RADICAL PARA ANDROID) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* FONDO BASE Y PARTÍCULAS */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important;
        background-image: radial-gradient(circle at 20% 30%, rgba(255, 75, 75, 0.08) 0%, transparent 25%),
                          radial-gradient(circle at 80% 70%, rgba(255, 75, 75, 0.08) 0%, transparent 25%),
                          radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 30px 30px !important;
    }

    /* FLECHA DE RESCATE (FIJA, ROJA Y POR ENCIMA DE TODO) */
    section[data-testid="stSidebar"] + div, [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0 15px 15px 0 !important;
        left: 0px !important;
        top: 15px !important;
        width: 60px !important;
        height: 55px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 10000000 !important;
        position: fixed !important;
        box-shadow: 5px 0 20px rgba(255, 0, 0, 0.5) !important;
    }
    
    /* Icono de la flecha siempre blanco */
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        width: 30px !important;
        height: 30px !important;
    }

    /* BARRA LATERAL CRISTAL iOS 26 */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 12, 15, 0.6) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* MENSAJES CRISTAL */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        margin-bottom: 12px !important;
    }

    /* TÍTULO NEÓN */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 3.5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 0.8rem; }
    .ruth-subtitle { text-align: center; color: #666; font-size: 0.7rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem; font-weight: bold;}

    /* BOTONES GHOST */
    .stButton>button { 
        border: none !important; background-color: transparent !important; color: #888 !important; 
        width: 100% !important; transition: 0.2s; text-transform: uppercase; font-size: 0.5rem !important; 
    }
    .stButton>button:hover { color: #ff4b4b !important; text-shadow: 0 0 10px #f00; }

    /* LOGIN MINIMALISTA */
    div[data-testid="stTextInput"] label { display: none !important; }
    div[data-testid="stTextInput"] input { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 12px !important; text-align: center; height: 45px !important;
    }
    
    [data-testid="stHeader"], footer { visibility: hidden !important; display: none !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
ruth_avatar = "logo_ruth.png" if os.path.exists("logo_ruth.png") else "●"

# --- 3. GESTIÓN DE ACCESO (LOGIN/REGISTRO LOCAL) ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"

def login_ui():
    st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([0.5, 2, 0.5])
    with col_c:
        if st.session_state.auth_mode == "login":
            u = st.text_input("U", placeholder="USUARIO", key="l_u")
            p = st.text_input("P", type="password", placeholder="CONTRASEÑA", key="l_p")
            if st.button("ACCEDER"):
                res = supabase.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.logged_in = True; st.session_state.user_name = u; st.rerun()
                else: st.error("Acceso incorrecto.")
            if st.button("CREAR CUENTA"):
                st.session_state.auth_mode = "signup"; st.rerun()
        else:
            nu = st.text_input("NU", placeholder="NUEVO SOCIO", key="s_u")
            np = st.text_input("NP", type="password", placeholder="NUEVA CLAVE", key="s_p")
            if st.button("REGISTRARME"):
                try:
                    supabase.table("usuarios").insert({"username": nu, "password": np}).execute()
                    st.success("Listo."); time.sleep(1); st.session_state.auth_mode = "login"; st.rerun()
                except: st.error("No disponible.")
            if st.button("VOLVER"):
                st.session_state.auth_mode = "login"; st.rerun()

if not st.session_state.logged_in:
    login_ui(); st.stop()

# --- 4. BARRA LATERAL (CONTROL CENTER) ---
with st.sidebar:
    st.markdown(f"<h3 style='color: white; font-weight: 100; text-align:center;'>{st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []; st.rerun()
    if st.button("SALIR"):
        st.session_state.logged_in = False; st.rerun()
    
    st.divider()
    # DICCIONARIOS
    ESPECIALIDADES = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO Advisor.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA Pro.", "Seguridad": "Seguridad."}
    TONOS = {"Analítica": "Fría.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}
    
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:20].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}"): # SIN ICONOS
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
if "messages" not in st.session_state: st.session_state.messages = []

# Botones Ghost (8 Especialidades)
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
