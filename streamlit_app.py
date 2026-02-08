import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA iOS 26 CRYSTAL PREMIUM ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* IMPORTAR FUENTE MODERNA */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* FONDO NEGRO CON GRADIENTE SUTIL */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* PARTÍCULAS DE FONDO */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(255, 75, 75, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(75, 75, 255, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* FLECHA DE RESCATE MEJORADA */
    [data-testid="stSidebarCollapsedControl"] {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff1744 100%) !important;
        color: white !important;
        border-radius: 0 15px 15px 0 !important;
        width: 45px !important;
        height: 45px !important;
        top: 20px !important;
        box-shadow: 0 8px 32px rgba(255, 75, 75, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        width: 50px !important;
        box-shadow: 0 12px 48px rgba(255, 75, 75, 0.6) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg { fill: white !important; }

    /* BARRA LATERAL CRISTAL PREMIUM */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 15, 0.6) !important;
        backdrop-filter: blur(40px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* ELEMENTOS DE LA SIDEBAR */
    [data-testid="stSidebar"] h3 {
        background: linear-gradient(135deg, #ffffff 0%, #b0b0b0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 200 !important;
        letter-spacing: 0.3rem !important;
        margin: 2rem 0 !important;
    }

    /* SELECTORES ESTILO iOS */
    [data-testid="stSidebar"] .stSelectbox {
        margin: 1rem 0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #888 !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.8rem !important;
        color: white !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(255, 75, 75, 0.3) !important;
        box-shadow: 0 4px 16px rgba(255, 75, 75, 0.1) !important;
    }

    /* MENSAJES DE CRISTAL MEJORADOS */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        margin: 1.5rem 0 !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3) !important;
    }

    /* TÍTULO NEÓN PREMIUM */
    @keyframes glow {
        0%, 100% { 
            text-shadow: 
                0 0 10px rgba(255, 75, 75, 0.8),
                0 0 20px rgba(255, 75, 75, 0.6),
                0 0 30px rgba(255, 75, 75, 0.4),
                0 0 40px rgba(255, 75, 75, 0.2);
        }
        50% { 
            text-shadow: 
                0 0 20px rgba(255, 75, 75, 1),
                0 0 30px rgba(255, 75, 75, 0.8),
                0 0 40px rgba(255, 75, 75, 0.6),
                0 0 60px rgba(255, 75, 75, 0.4);
        }
    }
    .ruth-header {
        text-align: center;
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8a80 50%, #ff4b4b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(2rem, 5vw, 3.5rem);
        animation: glow 3s ease-in-out infinite;
        font-weight: 100;
        letter-spacing: clamp(0.3rem, 2vw, 0.8rem);
        margin: 2rem 0 0.5rem 0;
        font-family: 'Inter', sans-serif;
    }
    .ruth-subtitle {
        text-align: center;
        color: #666;
        font-size: clamp(0.5rem, 1.5vw, 0.7rem);
        letter-spacing: 0.3rem;
        margin-bottom: 3rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* BOTONES ESPECIALIDAD PREMIUM */
    .stButton>button {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        color: #999 !important;
        padding: 1.2rem 1rem !important;
        font-size: 0.65rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.15rem !important;
        text-transform: uppercase !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* EFECTO HOVER EN BOTONES */
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 75, 75, 0.1);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    .stButton>button:hover {
        background: rgba(255, 75, 75, 0.08) !important;
        border-color: rgba(255, 75, 75, 0.4) !important;
        color: #ff4b4b !important;
        transform: translateY(-4px) !important;
        box-shadow: 
            0 8px 32px rgba(255, 75, 75, 0.2),
            0 0 0 1px rgba(255, 75, 75, 0.1) inset !important;
    }
    .stButton>button:active {
        transform: translateY(-2px) !important;
    }

    /* BOTONES DE SIDEBAR */
    [data-testid="stSidebar"] .stButton>button {
        width: 100% !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding: 0.9rem !important;
        font-size: 0.7rem !important;
        margin: 0.5rem 0 !important;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255, 75, 75, 0.1) !important;
        border-color: rgba(255, 75, 75, 0.3) !important;
    }

    /* INPUT DE CHAT MEJORADO */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 1rem !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(255, 75, 75, 0.3) !important;
        box-shadow: 0 8px 32px rgba(255, 75, 75, 0.15) !important;
    }

    /* LOGIN PREMIUM */
    div[data-testid="stTextInput"] input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        text-align: center !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.1rem !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255, 75, 75, 0.4) !important;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.2) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    /* DIVISORES ELEGANTES */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent) !important;
        margin: 2rem 0 !important;
    }

    /* OCULTAR ELEMENTOS STREAMLIT */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* SCROLLBAR PERSONALIZADA */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 75, 75, 0.3);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 75, 75, 0.5);
    }

    /* RESPONSIVE MEJORADO */
    @media (max-width: 768px) {
        .ruth-header { font-size: 2rem !important; letter-spacing: 0.3rem !important; }
        .ruth-subtitle { font-size: 0.5rem !important; }
        .stButton>button { font-size: 0.5rem !important; padding: 1rem 0.5rem !important; }
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
    
    # Espaciado vertical
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([0.3, 2, 0.3])
    with col_c:
        if st.session_state.auth_mode == "login":
            st.markdown("<br>", unsafe_allow_html=True)
            u = st.text_input("U", placeholder="USUARIO", key="l_u")
            p = st.text_input("P", type="password", placeholder="CONTRASEÑA", key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("ENTRAR", use_container_width=True):
                res = supabase.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u
                    st.rerun()
                else:
                    st.error("❌ Acceso denegado")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("CREAR CUENTA", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            nu = st.text_input("NU", placeholder="NUEVO SOCIO", key="s_u")
            np = st.text_input("NP", type="password", placeholder="NUEVA CLAVE", key="s_p")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("REGISTRARME", use_container_width=True):
                try:
                    supabase.table("usuarios").insert({"username": nu, "password": np}).execute()
                    st.success("✅ Cuenta creada")
                    time.sleep(1.5)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                except:
                    st.error("❌ Usuario ya existe")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("VOLVER AL LOGIN", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"<h3 style='color: white; font-weight: 200; text-align:center;'>{st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("＋ NUEVA"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("SALIR"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.divider()
    
    ESP = {
        "Abogada": "Abogada.",
        "Amazon Pro": "Amazon.",
        "Marketing": "Marketing.",
        "Estratega": "CEO Advisor.",
        "Médico": "Médico.",
        "Finanzas": "Finanzas.",
        "IA Pro": "IA Pro.",
        "Seguridad": "Seguridad."
    }
    
    TON = {
        "Analítica": "Fría.",
        "Sarcástica": "Cínica.",
        "Empática": "Suave.",
        "Motivadora": "Éxito.",
        "Ejecutiva": "ROI.",
        "Conspiranoica": "Oculto."
    }
    
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESP.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TON.keys()))
    
    st.divider()
    st.markdown("<p style='color: #666; font-size: 0.7rem; letter-spacing: 0.1rem; text-align: center;'>CONVERSACIONES RECIENTES</p>", unsafe_allow_html=True)
    
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:18].upper() if chat['messages'] else "VACÍO"
            if st.button(f"💬 {tit}...", key=chat['id']):
                st.session_state.messages = chat['messages']
                st.rerun()
    except:
        pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Grid de especialidades con mejor espaciado
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(4)
labels = list(ESP.keys())

for i in range(8):
    with cols[i % 4]:
        if st.button(labels[i].upper(), key=f"spec_{i}"):
            st.session_state.messages.append({"role": "user", "content": f"Ejecuta: {labels[i]}"})
            sys_i = f"Eres RUTH {ESP[labels[i]]} ({TON[ton_act]})."
            c = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_i}] + st.session_state.messages[-5:]
            )
            st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
            try:
                supabase.table("chats").insert({
                    "user_email": st.session_state.user_name,
                    "messages": st.session_state.messages
                }).execute()
            except:
                pass
            st.rerun()

st.divider()

# Mensajes del chat
for msg in st.session_state.messages:
    if "Ejecuta:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

# Input del chat
if prompt := st.chat_input(f"💭 Habla con RUTH {esp_act}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=ruth_avatar):
        sys_i = f"Identidad RUTH: {ESP[esp_act]} Tono: {TON[ton_act]}."
        c = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_i}] + st.session_state.messages[-5:],
            model="llama-3.3-70b-versatile"
        )
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        try:
            supabase.table("chats").insert({
                "user_email": st.session_state.user_name,
                "messages": st.session_state.messages
            }).execute()
        except:
            pass
