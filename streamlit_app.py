import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA (CSS BLINDADO) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium con Partículas */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(circle at 50% 50%, rgba(255, 75, 75, 0.02) 0%, transparent 80%),
                          radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 100% 100%, 30px 30px !important;
    }

    /* FLECHA DE RESCATE (REFORZADA) */
    button[kind="headerNoContext"], [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0 10px 10px 0 !important; left: 0 !important;
        top: 20px !important; width: 60px !important; height: 50px !important;
        display: flex !important; z-index: 9999999 !important;
        box-shadow: 5px 0 15px rgba(255, 75, 75, 0.4) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }

    /* TÍTULO NEÓN */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    .login-box { max-width: 400px; margin: auto; padding: 2rem; background: rgba(26, 29, 36, 0.9); border: 1px solid #ff4b4b; border-radius: 15px; text-align: center; }
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    .stButton>button:hover { color: #ff4b4b !important; text-shadow: 0 0 10px #ff0000; }
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

def mostrar_acceso():
    st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">ACCESO AL SISTEMA</div>', unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if st.session_state.auth_mode == "login":
            st.markdown("<h4 style='color:white;'>ENTRAR</h4>", unsafe_allow_html=True)
            u = st.text_input("USUARIO", key="login_u")
            p = st.text_input("CONTRASEÑA", type="password", key="login_p")
            if st.button("INICIAR SESIÓN"):
                res = supabase.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u
                    st.rerun()
                else: st.error("Credenciales incorrectas.")
            if st.button("CREAR UNA CUENTA NUEVA"):
                st.session_state.auth_mode = "signup"; st.rerun()
        else:
            st.markdown("<h4 style='color:white;'>REGISTRO</h4>", unsafe_allow_html=True)
            new_u = st.text_input("USUARIO NUEVO", key="sign_u")
            new_p = st.text_input("CONTRASEÑA NUEVA", type="password", key="sign_p")
            if st.button("REGISTRARME"):
                try:
                    supabase.table("usuarios").insert({"username": new_u, "password": new_p}).execute()
                    st.success("¡Cuenta creada!"); time.sleep(1); st.session_state.auth_mode = "login"; st.rerun()
                except: st.error("El usuario ya existe.")
            if st.button("VOLVER"): st.session_state.auth_mode = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    mostrar_acceso()
    st.stop()

# --- 4. BARRA LATERAL (CONTROL CENTER) ---
with st.sidebar:
    st.markdown(f"<h3 style='color: white; font-weight: 200;'>SOCIO: {st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    
    # REINCORPORACIÓN DEL BOTÓN DE NUEVA CONVERSACIÓN
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            try: supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
            except: pass
        st.session_state.messages = []
        st.rerun()

    if st.button("CERRAR SESIÓN"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    ESPECIALIDADES = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA.", "Seguridad": "Seguridad."}
    TONOS = {"Analítica": "Lógica.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            tit = "VACÍO"
            for m in chat['messages']:
                if m['role'] == 'user': tit = m['content'][:15].upper() + "..."; break
            if st.button(f"{tit}", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []

# Botones Ghost
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Acción: {labels[i]}"})
            sys_i = f"Identidad: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}."
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
        sys_i = f"Identidad RUTH: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}."
        c = client.chat.completions.create(messages=[{"role":"system","content": sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
        try: supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
        except: pass
