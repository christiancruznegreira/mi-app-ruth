import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time
import urllib.parse

# --- FUNCIÓN PARA DETECTAR Y GENERAR IMÁGENES ---
def detectar_pedido_imagen(texto):
    palabras_clave = [
        'genera una imagen', 'crea una imagen', 'genera un', 'crea un',
        'muéstrame', 'dibuja', 'diseña', 'imagen de', 'foto de',
        'logo de', 'ilustra', 'render', 'visualiza'
    ]
    texto_lower = texto.lower()
    return any(palabra in texto_lower for palabra in palabras_clave)

def generar_imagen(prompt_texto):
    prompt_limpio = prompt_texto.lower()
    for palabra in ['genera una imagen de', 'crea una imagen de', 'genera un', 'crea un', 
                    'muéstrame', 'dibuja', 'diseña', 'imagen de', 'foto de', 'logo de']:
        prompt_limpio = prompt_limpio.replace(palabra, '')
    
    prompt_limpio = prompt_limpio.strip()
    prompt_encoded = urllib.parse.quote(prompt_limpio)
    imagen_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"
    
    return imagen_url, prompt_limpio

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="RUTH", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* FUENTES PROFESIONALES - SF PRO DISPLAY */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* FONDO CON TEXTURA PROFESIONAL */
    .stApp {
        background: 
            linear-gradient(135deg, rgba(255, 59, 48, 0.03) 0%, transparent 50%),
            linear-gradient(180deg, #0a0a0a 0%, #000000 50%, #0a0a0a 100%) !important;
        background-attachment: fixed !important;
        position: relative !important;
    }
    
    /* PATRÓN DE PUNTOS SUTIL */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: radial-gradient(circle, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }
    
    /* FLECHA SIDEBAR - ICONO REAL SVG */
    [data-testid="stSidebarCollapsedControl"] {
        background: linear-gradient(135deg, #ff3b30 0%, #ff2d55 100%) !important;
        border: none !important;
        border-radius: 0 14px 14px 0 !important;
        width: 44px !important;
        height: 44px !important;
        top: 20px !important;
        box-shadow: 
            0 4px 12px rgba(255, 59, 48, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: linear-gradient(135deg, #ff453a 0%, #ff375f 100%) !important;
        transform: translateX(2px) scale(1.05) !important;
        box-shadow: 
            0 6px 20px rgba(255, 59, 48, 0.6),
            0 0 0 1px rgba(255, 255, 255, 0.15) inset !important;
    }
    
    /* FORZAR SOLO ICONO SVG - OCULTAR TEXTO */
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        width: 24px !important;
        height: 24px !important;
        display: block !important;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)) !important;
    }
    [data-testid="stSidebarCollapsedControl"] * {
        color: transparent !important;
        font-size: 0 !important;
    }
    [data-testid="stSidebarCollapsedControl"] span,
    [data-testid="stSidebarCollapsedControl"] p,
    [data-testid="stSidebarCollapsedControl"] div {
        display: none !important;
    }

    /* SIDEBAR PREMIUM */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%) !important;
        border-right: 1px solid rgba(255, 59, 48, 0.2) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #ff3b30 !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        letter-spacing: 2px !important;
        text-align: center !important;
        margin: 32px 0 24px 0 !important;
        text-shadow: 0 0 20px rgba(255, 59, 48, 0.5) !important;
    }

    /* LABELS SÚPER VISIBLES */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
        display: block !important;
        opacity: 1 !important;
    }
    
    /* SELECTORES CON TEXTO VISIBLE */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: rgba(30, 30, 30, 0.8) !important;
        border: 1.5px solid rgba(255, 59, 48, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {
        background: rgba(40, 40, 40, 0.9) !important;
        border-color: rgba(255, 59, 48, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(255, 59, 48, 0.1) !important;
    }
    
    /* TEXTO DENTRO DEL SELECTOR - BLANCO BRILLANTE */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
    }
    
    /* DROPDOWN MENU */
    div[role="listbox"] {
        background: #1a1a1a !important;
        border: 1.5px solid rgba(255, 59, 48, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }
    
    /* OPTIONS EN DROPDOWN - BLANCO */
    div[role="option"] {
        color: #ffffff !important;
        background: transparent !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    div[role="option"]:hover {
        background: rgba(255, 59, 48, 0.15) !important;
        color: #ff3b30 !important;
    }
    div[role="option"][aria-selected="true"] {
        background: rgba(255, 59, 48, 0.2) !important;
        color: #ff3b30 !important;
        font-weight: 600 !important;
    }

    /* MENSAJES PROFESIONALES */
    [data-testid="stChatMessage"] {
        background: rgba(26, 26, 26, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-left: 3px solid #ff3b30 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin: 20px 0 !important;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.02) inset !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(30, 30, 30, 0.9) !important;
        border-left-color: #ff453a !important;
        transform: translateX(4px) !important;
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(255, 59, 48, 0.1) inset !important;
    }
    [data-testid="stChatMessage"] p {
        color: #f0f0f0 !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
        font-weight: 400 !important;
        letter-spacing: 0.2px !important;
    }

    /* TÍTULO NEÓN PROFESIONAL */
    @keyframes neon-breathe {
        0%, 100% {
            text-shadow: 
                0 0 10px rgba(255, 59, 48, 0.6),
                0 0 20px rgba(255, 59, 48, 0.4),
                0 0 30px rgba(255, 59, 48, 0.2),
                0 0 40px rgba(255, 59, 48, 0.1);
        }
        50% {
            text-shadow: 
                0 0 20px rgba(255, 59, 48, 0.9),
                0 0 30px rgba(255, 59, 48, 0.6),
                0 0 40px rgba(255, 59, 48, 0.4),
                0 0 60px rgba(255, 59, 48, 0.2);
        }
    }
    
    .ruth-header {
        text-align: center;
        background: linear-gradient(135deg, #ff3b30 0%, #ff2d55 50%, #ff3b30 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: clamp(52px, 10vw, 88px);
        font-weight: 800 !important;
        letter-spacing: clamp(12px, 4vw, 28px);
        margin: clamp(40px, 8vh, 72px) 0 clamp(12px, 2vh, 20px) 0;
        animation: neon-breathe 4s ease-in-out infinite;
        line-height: 1;
        filter: drop-shadow(0 4px 24px rgba(255, 59, 48, 0.4));
    }
    
    .ruth-subtitle {
        text-align: center;
        color: #999;
        font-size: clamp(10px, 1.5vw, 13px);
        font-weight: 600 !important;
        letter-spacing: clamp(3px, 1.5vw, 5px);
        margin-bottom: clamp(40px, 7vh, 56px);
        text-transform: uppercase;
    }

    /* BOTONES PROFESIONALES */
    .stButton>button {
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.6) 0%, rgba(20, 20, 20, 0.8) 100%) !important;
        backdrop-filter: blur(10px) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        color: #e0e0e0 !important;
        padding: 18px 24px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.03) inset !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(255, 59, 48, 0.15) 0%, rgba(255, 45, 85, 0.2) 100%) !important;
        border-color: rgba(255, 59, 48, 0.4) !important;
        color: #ff3b30 !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 
            0 8px 24px rgba(255, 59, 48, 0.25),
            0 0 0 1px rgba(255, 59, 48, 0.1) inset !important;
    }
    .stButton>button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }

    [data-testid="stSidebar"] .stButton>button {
        padding: 14px 16px !important;
        font-size: 12px !important;
        margin: 8px 0 !important;
    }
    
    .delete-history-btn button {
        background: linear-gradient(135deg, rgba(255, 59, 48, 0.15) 0%, rgba(255, 45, 85, 0.2) 100%) !important;
        border: 1.5px solid rgba(255, 59, 48, 0.4) !important;
        color: #ff3b30 !important;
    }
    .delete-history-btn button:hover {
        background: linear-gradient(135deg, rgba(255, 59, 48, 0.25) 0%, rgba(255, 45, 85, 0.3) 100%) !important;
        border-color: rgba(255, 59, 48, 0.6) !important;
    }

    /* INPUT CHAT PROFESIONAL */
    [data-testid="stChatInput"] {
        background: rgba(26, 26, 26, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px !important;
        padding: 4px !important;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.02) inset !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(255, 59, 48, 0.5) !important;
        box-shadow: 
            0 4px 20px rgba(255, 59, 48, 0.2),
            0 0 0 4px rgba(255, 59, 48, 0.08) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #f0f0f0 !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        letter-spacing: 0.3px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #666 !important;
    }

    /* LOGIN PROFESIONAL */
    div[data-testid="stTextInput"] input {
        background: rgba(26, 26, 26, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        color: #f0f0f0 !important;
        padding: 18px !important;
        text-align: center !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        letter-spacing: 1.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.02) inset !important;
    }
    div[data-testid="stTextInput"] input:focus {
        background: rgba(30, 30, 30, 0.9) !important;
        border-color: rgba(255, 59, 48, 0.5) !important;
        outline: none !important;
        box-shadow: 
            0 0 0 4px rgba(255, 59, 48, 0.1),
            0 0 0 1px rgba(255, 59, 48, 0.1) inset !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #666 !important;
        font-weight: 400 !important;
    }
    div[data-testid="stTextInput"] label { 
        display: none !important; 
    }

    /* IMAGEN GENERADA */
    .generated-image {
        border: 2px solid rgba(255, 59, 48, 0.4) !important;
        border-radius: 16px !important;
        box-shadow: 
            0 8px 32px rgba(255, 59, 48, 0.3),
            0 0 0 1px rgba(255, 59, 48, 0.2) inset !important;
        margin: 20px 0 !important;
    }

    /* DIVISOR ELEGANTE */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 59, 48, 0.1) 20%,
            rgba(255, 59, 48, 0.3) 50%,
            rgba(255, 59, 48, 0.1) 80%,
            transparent 100%) !important;
        margin: 40px 0 !important;
        box-shadow: 0 0 20px rgba(255, 59, 48, 0.2) !important;
    }

    /* OCULTAR ELEMENTOS STREAMLIT */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* SCROLLBAR PREMIUM */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
        border-left: 1px solid rgba(255, 255, 255, 0.05);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ff3b30 0%, #ff2d55 100%);
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(255, 59, 48, 0.5);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ff453a 0%, #ff375f 100%);
    }

    /* MENSAJES ERROR/SUCCESS */
    .stSuccess, .stError {
        background: rgba(26, 26, 26, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1.5px solid rgba(255, 59, 48, 0.4) !important;
        border-radius: 12px !important;
        color: #ff3b30 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 16px !important;
        box-shadow: 0 4px 16px rgba(255, 59, 48, 0.2) !important;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .ruth-header {
            font-size: 40px !important;
            letter-spacing: 8px !important;
            margin: 32px 0 12px 0 !important;
        }
        .ruth-subtitle {
            font-size: 9px !important;
            letter-spacing: 2px !important;
        }
        .stButton>button {
            padding: 16px 14px !important;
            font-size: 12px !important;
        }
        [data-testid="stSidebar"] {
            width: 85vw !important;
        }
        [data-testid="stChatMessage"] {
            padding: 18px !important;
        }
    }
    
    @media (max-width: 480px) {
        .ruth-header {
            font-size: 32px !important;
            letter-spacing: 6px !important;
        }
        .stButton>button {
            padding: 14px 10px !important;
            font-size: 11px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
ruth_avatar = "logo_ruth.png" if os.path.exists("logo_ruth.png") else "●"

# --- GESTIÓN DE ACCESO ---
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
if "user_name" not in st.session_state: 
    st.session_state.user_name = ""
if "auth_mode" not in st.session_state: 
    st.session_state.auth_mode = "login"

def login_ui():
    st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE · IA VISUAL</div>', unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([0.3, 2, 0.3])
    with col_c:
        if st.session_state.auth_mode == "login":
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
                    st.error("Acceso denegado")
            
            if st.button("CREAR CUENTA", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
        else:
            nu = st.text_input("NU", placeholder="USUARIO", key="s_u")
            np = st.text_input("NP", type="password", placeholder="CONTRASEÑA", key="s_p")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("REGISTRAR", use_container_width=True):
                try:
                    supabase.table("usuarios").insert({"username": nu, "password": np}).execute()
                    st.success("Cuenta creada exitosamente")
                    time.sleep(1.5)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                except:
                    st.error("Usuario ya existe")
            
            if st.button("VOLVER", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# --- BARRA LATERAL ---
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
    
    esp_act = st.selectbox("ESPECIALIDAD", list(ESP.keys()), key="esp_select")
    ton_act = st.selectbox("PERSONALIDAD", list(TON.keys()), key="ton_select")
    
    st.divider()
    
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(6).execute()
        if res.data:
            st.markdown("<p style='color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 12px;'>HISTORIAL</p>", unsafe_allow_html=True)
            
            st.markdown('<div class="delete-history-btn">', unsafe_allow_html=True)
            if st.button("🗑️ BORRAR TODO"):
                try:
                    supabase.table("chats").delete().eq("user_email", st.session_state.user_name).execute()
                    st.success("Historial eliminado")
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("Error al borrar")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            for chat in res.data:
                tit = chat['messages'][0]['content'][:18].upper() if chat['messages'] else "VACÍO"
                if st.button(f"💬 {tit}...", key=chat['id']):
                    st.session_state.messages = chat['messages']
                    st.rerun()
    except:
        pass

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE · IA VISUAL</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

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

for msg in st.session_state.messages:
    if "Ejecuta:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            if msg["role"] == "assistant" and "![IMAGEN](" in msg["content"]:
                partes = msg["content"].split("![IMAGEN](")
                st.markdown(partes[0])
                url_imagen = partes[1].split(")")[0]
                st.markdown(f'<img src="{url_imagen}" class="generated-image" style="width: 100%; max-width: 600px; border-radius: 16px;">', unsafe_allow_html=True)
                if len(partes[1].split(")")) > 1:
                    st.markdown(partes[1].split(")", 1)[1])
            else:
                st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=ruth_avatar):
        if detectar_pedido_imagen(prompt):
            imagen_url, prompt_limpio = generar_imagen(prompt)
            respuesta = f"✨ Imagen generada: **{prompt_limpio}**\n\n![IMAGEN]({imagen_url})\n\n*Generado con IA visual de RUTH*"
            
            st.markdown(f"✨ Imagen generada: **{prompt_limpio}**")
            st.markdown(f'<img src="{imagen_url}" class="generated-image" style="width: 100%; max-width: 600px; border-radius: 16px;">', unsafe_allow_html=True)
            st.markdown("*Generado con IA visual de RUTH*")
            
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        else:
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
