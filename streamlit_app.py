import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time

# --- 1. CONFIGURACIÓN Y ESTÉTICA CYBERPUNK MINIMALISTA ---
st.set_page_config(page_title="RUTH", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* FUENTE MONOESPACIADA CYBERPUNK */
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Space Mono', monospace !important;
    }
    
    /* FONDO NEGRO PURO */
    .stApp {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* FLECHA SIDEBAR MINIMALISTA */
    [data-testid="stSidebarCollapsedControl"] {
        background: #ff0000 !important;
        border: none !important;
        border-radius: 0 8px 8px 0 !important;
        width: 40px !important;
        height: 40px !important;
        top: 15px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: #cc0000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg { 
        fill: white !important;
    }

    /* SIDEBAR NEGRA CON BORDE ROJO */
    [data-testid="stSidebar"] {
        background: #000000 !important;
        border-right: 1px solid #ff0000 !important;
    }
    
    /* ELEMENTOS SIDEBAR */
    [data-testid="stSidebar"] h3 {
        color: #ff0000 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5rem !important;
        text-align: center !important;
        margin: 2rem 0 !important;
        font-size: 1.2rem !important;
    }

    /* SELECTORES MINIMALISTAS */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #666 !important;
        font-size: 0.65rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.2rem !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: transparent !important;
        border: 1px solid #333 !important;
        border-radius: 0 !important;
        color: #fff !important;
        padding: 0.6rem !important;
        font-size: 0.8rem !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: #ff0000 !important;
    }

    /* MENSAJES MINIMALISTAS */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: 1px solid #1a1a1a !important;
        border-left: 3px solid #ff0000 !important;
        border-radius: 0 !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }
    [data-testid="stChatMessage"]:hover {
        border-left-color: #ff3333 !important;
        background: #0a0a0a !important;
    }

    /* TÍTULO NEÓN PARPADEO MATRIZ */
    @keyframes neon-flicker {
        0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {
            opacity: 1;
            text-shadow: 
                0 0 10px #ff0000,
                0 0 20px #ff0000,
                0 0 40px #ff0000,
                0 0 80px #ff0000;
        }
        20%, 21.999%, 63%, 63.999%, 65%, 69.999% {
            opacity: 0.4;
            text-shadow: none;
        }
    }
    
    .ruth-header {
        text-align: center;
        color: #ff0000;
        font-size: clamp(2.5rem, 8vw, 5rem);
        font-weight: 700;
        letter-spacing: clamp(0.5rem, 3vw, 1.5rem);
        margin: clamp(1rem, 4vh, 3rem) 0 clamp(0.5rem, 2vh, 1rem) 0;
        animation: neon-flicker 5s infinite;
        line-height: 1;
    }
    
    .ruth-subtitle {
        text-align: center;
        color: #666;
        font-size: clamp(0.45rem, 1.2vw, 0.6rem);
        letter-spacing: clamp(0.2rem, 1vw, 0.4rem);
        margin-bottom: clamp(1.5rem, 4vh, 3rem);
        font-weight: 400;
        text-transform: uppercase;
    }

    /* BOTONES ULTRA MINIMALISTAS */
    .stButton>button {
        background: transparent !important;
        border: 1px solid #333 !important;
        border-radius: 0 !important;
        color: #999 !important;
        padding: clamp(0.8rem, 2.5vw, 1rem) clamp(0.5rem, 2vw, 0.8rem) !important;
        font-size: clamp(0.5rem, 1.5vw, 0.65rem) !important;
        font-weight: 400 !important;
        letter-spacing: 0.15rem !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stButton>button:hover {
        background: transparent !important;
        border-color: #ff0000 !important;
        color: #ff0000 !important;
    }
    
    .stButton>button:active {
        background: rgba(255, 0, 0, 0.1) !important;
    }

    /* BOTONES SIDEBAR */
    [data-testid="stSidebar"] .stButton>button {
        margin: 0.3rem 0 !important;
        padding: 0.7rem !important;
        font-size: 0.65rem !important;
    }

    /* INPUT CHAT MINIMALISTA */
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: 1px solid #333 !important;
        border-radius: 0 !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #ff0000 !important;
    }
    [data-testid="stChatInput"] textarea {
        color: white !important;
        font-size: clamp(0.8rem, 2vw, 0.9rem) !important;
    }

    /* LOGIN MINIMALISTA */
    div[data-testid="stTextInput"] input {
        background: transparent !important;
        border: 1px solid #333 !important;
        border-radius: 0 !important;
        color: #fff !important;
        padding: 1rem !important;
        text-align: center !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.2rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #ff0000 !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] label { 
        display: none !important; 
    }

    /* DIVISORES ROJOS */
    hr {
        border: none !important;
        height: 1px !important;
        background: #ff0000 !important;
        margin: clamp(1rem, 3vh, 2rem) 0 !important;
        opacity: 0.3;
    }

    /* OCULTAR ELEMENTOS */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* SCROLLBAR ROJA */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #ff0000;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #cc0000;
    }

    /* MENSAJES DE ERROR/SUCCESS */
    .stSuccess, .stError {
        background: transparent !important;
        border: 1px solid #ff0000 !important;
        border-radius: 0 !important;
        color: #ff0000 !important;
        font-size: 0.8rem !important;
        padding: 0.8rem !important;
    }

    /* RESPONSIVE MOBILE PERFECTO */
    @media (max-width: 768px) {
        /* Título más pequeño en móvil */
        .ruth-header {
            font-size: 2rem !important;
            letter-spacing: 0.4rem !important;
            margin: 1.5rem 0 0.5rem 0 !important;
        }
        
        .ruth-subtitle {
            font-size: 0.4rem !important;
            letter-spacing: 0.15rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        /* Botones más compactos */
        .stButton>button {
            padding: 0.8rem 0.3rem !important;
            font-size: 0.5rem !important;
            letter-spacing: 0.08rem !important;
        }
        
        /* Grid de 2 columnas en móvil */
        [data-testid="column"] {
            padding: 0.2rem !important;
        }
        
        /* Mensajes más compactos */
        [data-testid="stChatMessage"] {
            padding: 0.8rem !important;
            margin: 0.5rem 0 !important;
            font-size: 0.85rem !important;
        }
        
        /* Sidebar más estrecha */
        [data-testid="stSidebar"] {
            width: 85vw !important;
        }
        
        /* Input más grande para touch */
        [data-testid="stChatInput"] textarea {
            font-size: 1rem !important;
            padding: 0.8rem !important;
        }
        
        /* Selectores más grandes */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            padding: 0.8rem !important;
            font-size: 0.85rem !important;
        }
    }
    
    /* TABLETS (768px - 1024px) */
    @media (min-width: 768px) and (max-width: 1024px) {
        .ruth-header {
            font-size: 3rem !important;
            letter-spacing: 0.6rem !important;
        }
        
        .stButton>button {
            font-size: 0.58rem !important;
            padding: 0.9rem 0.6rem !important;
        }
    }
    
    /* PANTALLAS PEQUEÑAS (<480px) */
    @media (max-width: 480px) {
        .ruth-header {
            font-size: 1.8rem !important;
            letter-spacing: 0.3rem !important;
            margin: 1rem 0 0.5rem 0 !important;
        }
        
        .ruth-subtitle {
            font-size: 0.35rem !important;
            letter-spacing: 0.1rem !important;
        }
        
        .stButton>button {
            padding: 0.7rem 0.2rem !important;
            font-size: 0.45rem !important;
            letter-spacing: 0.05rem !important;
        }
        
        [data-testid="stChatMessage"] {
            padding: 0.6rem !important;
            font-size: 0.8rem !important;
        }
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
    st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([0.2, 2, 0.2])
    with col_c:
        if st.session_state.auth_mode == "login":
            u = st.text_input("U", placeholder="USUARIO", key="l_u")
            p = st.text_input("P", type="password", placeholder="CONTRASEÑA", key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("ENTRAR"):
                res = supabase.table("usuarios").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u
                    st.rerun()
                else:
                    st.error("ACCESO DENEGADO")
            
            if st.button("CREAR CUENTA"):
                st.session_state.auth_mode = "signup"
                st.rerun()
        else:
            nu = st.text_input("NU", placeholder="USUARIO", key="s_u")
            np = st.text_input("NP", type="password", placeholder="CONTRASEÑA", key="s_p")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("REGISTRAR"):
                try:
                    supabase.table("usuarios").insert({"username": nu, "password": np}).execute()
                    st.success("CUENTA CREADA")
                    time.sleep(1)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                except:
                    st.error("USUARIO EXISTENTE")
            
            if st.button("VOLVER"):
                st.session_state.auth_mode = "login"
                st.rerun()

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"<h3>{st.session_state.user_name.upper()}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ NUEVA"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("SALIR"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.divider()
    
    ESP = {
        "Abogada": "Abogada.",
        "Amazon": "Amazon.",
        "Marketing": "Marketing.",
        "Estratega": "CEO.",
        "Médico": "Médico.",
        "Finanzas": "Finanzas.",
        "IA": "IA Pro.",
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
    
    esp_act = st.selectbox("Especialidad", list(ESP.keys()))
    ton_act = st.selectbox("Personalidad", list(TON.keys()))
    
    st.divider()
    
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(6).execute()
        if res.data:
            st.markdown("<p style='color: #666; font-size: 0.6rem; letter-spacing: 0.1rem; margin-bottom: 0.5rem;'>HISTORIAL</p>", unsafe_allow_html=True)
            for chat in res.data:
                tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
                if st.button(f"{tit}...", key=chat['id']):
                    st.session_state.messages = chat['messages']
                    st.rerun()
    except:
        pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Grid responsive: 4 columnas desktop, 2 móvil
cols = st.columns(4)
labels = list(ESP.keys())

for i in range(8):
    with cols[i % 4]:
        if st.button(labels[i].upper(), key=f"btn_{i}"):
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

# Chat
for msg in st.session_state.messages:
    if "Ejecuta:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input("MENSAJE"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=ruth_avatar):
        sys_i = f"Eres RUTH {ESP[esp_act]} ({TON[ton_act]})."
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
