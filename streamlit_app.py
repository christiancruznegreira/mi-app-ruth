import streamlit as st
from groq import Groq
from supabase import create_client, Client
from streamlit_google_auth import Authenticate
import os
import datetime

# --- 1. ESTÉTICA PREMIUM RUTH ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0; text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4);}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}
    .stButton>button { border-radius: 15px !important; border: 1px solid #ff4b4b !important; background-color: rgba(255, 75, 75, 0.05) !important; color: white !important; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #ff4b4b !important; box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE LOGIN (CORREGIDO PARA EVITAR TYPEERROR) ---
# Extraemos los datos manualmente de los Secrets
google_creds = st.secrets["GOOGLE_AUTH"]

auth = Authenticate(
    secret_name='GOOGLE_AUTH',
    client_id=google_creds['client_id'],
    client_secret=google_creds['client_secret'],
    redirect_uri=google_creds['redirect_uri'],
    cookie_name='ruth_session_cookie',
    key=google_creds['cookie_key'],
    cookie_expiry_days=30,
)

auth.check_authenticator()

if not st.session_state.get('connected'):
    st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white; font-weight: 200; margin-top: 50px;'>Acceso al Ecosistema</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth.login() 
    st.stop()

# --- SI ESTÁ CONECTADO, OBTENEMOS DATOS ---
user_email = st.session_state['user_info'].get('email')
user_name = st.session_state['user_info'].get('name', 'Profesional')

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

EXPERTOS = {
    "Abogada": "Eres RUTH Abogada Senior. Rigurosa y técnica.",
    "Amazon Pro": "Eres RUTH Amazon Experta. Comercial y estratégica.",
    "Marketing": "Eres RUTH Directora de Marketing. Creativa y persuasiva.",
    "Estratega": "Eres RUTH Business Estratega. Ejecutiva y fría."
}

def guardar_nube(mensajes):
    try: supabase.table("chats").insert({"user_email": user_email, "messages": mensajes}).execute()
    except: pass

def cargar_nube():
    try: 
        res = supabase.table("chats").select("*").eq("user_email", user_email).order("created_at", desc=True).limit(5).execute()
        return res.data
    except: return []

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"<p style='color: #ff4b4b; font-weight: bold;'>Hola, {user_name}</p>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Especialidad:", list(EXPERTOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.8rem;'>TU HISTORIAL EN NUBE</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        fecha = chat['created_at'][11:16]
        if st.button(f"📜 Chat {fecha}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()
    
    st.divider()
    if st.button("Cerrar Sesión"):
        auth.logout()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
st.markdown(f'<div class="ruth-subtitle">MÓDULO {modo.upper()} ACTIVO</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"¿En qué puede ayudarte RUTH hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(
            messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
