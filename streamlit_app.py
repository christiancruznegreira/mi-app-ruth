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
    /* FUENTE SISTEMA iOS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
    }
    
    /* FONDO NEGRO MATE PREMIUM */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%) !important;
        color: #f5f5f5 !important;
    }
    
    /* FLECHA SIDEBAR - ROJA */
    [data-testid="stSidebarCollapsedControl"] {
        background: #ff3b30 !important;
        border: none !important;
        border-radius: 0 12px 12px 0 !important;
        width: 40px !important;
        height: 40px !important;
        top: 16px !important;
        box-shadow: 0 4px 16px rgba(255, 59, 48, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: #ff453a !important;
        transform: scale(1.05) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
    }

    /* SIDEBAR ESTILO iOS */
    [data-testid="stSidebar"] {
        background: #1c1c1e !important;
        border-right: 1px solid #2c2c2e !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #ff3b30 !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-align: center !important;
        margin: 24px 0 !important;
        font-size: 18px !important;
    }

    /* LABELS VISIBLES */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #8e8e93 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
        display: block !important;
    }
    
    /* SELECTORES iOS STYLE - TEXTO VISIBLE */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #2c2c2e !important;
        border: 1px solid #3a3a3c !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        background: #3a3a3c !important;
        border-color: #ff3b30 !important;
    }
    
    /* DROPDOWN OPTIONS - TEXTO VISIBLE */
    [data-testid="stSidebar"] .stSelectbox div[role="listbox"] {
        background: #2c2c2e !important;
        border: 1px solid #3a3a3c !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[role="option"] {
        color: #ffffff !important;
        background: #2c2c2e !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[role="option"]:hover {
        background: #3a3a3c !important;
        color: #ff3b30 !important;
    }

    /* MENSAJES ESTILO CLAUDE */
    [data-testid="stChatMessage"] {
        background: #1c1c1e !important;
        border: 1px solid #2c2c2e !important;
        border-left: 3px solid #ff3b30 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin: 16px 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stChatMessage"]:hover {
        background: #2c2c2e !important;
        transform: translateX(4px) !important;
    }
    [data-testid="stChatMessage"] p {
        color: #f5f5f5 !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
    }

    /* TÍTULO NEÓN ROJO */
    @keyframes neon-pulse {
        0%, 100% {
            text-shadow: 
                0 0 10px rgba(255, 59, 48, 0.8),
                0 0 20px rgba(255, 59, 48, 0.6),
                0 0 30px rgba(255, 59, 48, 0.4);
        }
        50% {
            text-shadow: 
                0 0 20px rgba(255, 59, 48, 1),
                0 0 30px rgba(255, 59, 48, 0.8),
                0 0 40px rgba(255, 59, 48, 0.6);
        }
    }
    
    .ruth-header {
        text-align: center;
        color: #ff3b30;
        font-size: clamp(48px, 10vw, 80px);
        font-weight: 700 !important;
        letter-spacing: clamp(8px, 3vw, 24px);
        margin: clamp(32px, 8vh, 64px) 0 clamp(8px, 2vh, 16px) 0;
        animation: neon-pulse 3s ease-in-out infinite;
        line-height: 1;
    }
    
    .ruth-subtitle {
        text-align: center;
        color: #8e8e93;
        font-size: clamp(10px, 1.5vw, 13px);
        font-weight: 500 !important;
        letter-spacing: clamp(2px, 1vw, 4px);
        margin-bottom: clamp(32px, 6vh, 48px);
        text-transform: uppercase;
    }

    /* BOTONES iOS STYLE */
    .stButton>button {
        background: #1c1c1e !important;
        border: 1px solid #3a3a3c !important;
        border-radius: 12px !important;
        color: #f5f5f5 !important;
        padding: 16px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton>button:hover {
        background: #2c2c2e !important;
        border-color: #ff3b30 !important;
        color: #ff3b30 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 16px rgba(255, 59, 48, 0.2) !important;
    }

    [data-testid="stSidebar"] .stButton>button {
        padding: 12px !important;
        font-size: 13px !important;
        margin: 8px 0 !important;
    }
    
    .delete-history-btn button {
        background: rgba(255, 59, 48, 0.1) !important;
        border: 1px solid rgba(255, 59, 48, 0.3) !important;
        color: #ff3b30 !important;
    }
    .delete-history-btn button:hover {
        background: rgba(255, 59, 48, 0.2) !important;
    }

    /* INPUT CHAT iOS */
    [data-testid="stChatInput"] {
        background: #1c1c1e !important;
        border: 1px solid #3a3a3c !important;
        border-radius: 24px !important;
        padding: 4px !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #ff3b30 !important;
        box-shadow: 0 0 0 4px rgba(255, 59, 48, 0.1) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #f5f5f5 !important;
        font-size: 15px !important;
        font-weight: 400 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8e8e93 !important;
    }

    /* LOGIN iOS STYLE */
    div[data-testid="stTextInput"] input {
        background: #1c1c1e !important;
        border: 1px solid #3a3a3c !important;
        border-radius: 12px !important;
        color: #f5f5f5 !important;
        padding: 16px !important;
        text-align: center !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        background: #2c2c2e !important;
        border-color: #ff3b30 !important;
        outline: none !important;
        box-shadow: 0 0 0 4px rgba(255, 59, 48, 0.1) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #8e8e93 !important;
    }
    div[data-testid="stTextInput"] label { 
        display: none !important; 
    }

    /* IMAGEN GENERADA */
    .generated-image {
        border: 2px solid #ff3b30 !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(255, 59, 48, 0.3) !important;
        margin: 16px 0 !important;
    }

    /* DIVISOR ROJO */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #ff3b30, transparent) !important;
        margin: 32px 0 !important;
        opacity: 0.3 !important;
    }

    /* OCULTAR ELEMENTOS STREAMLIT */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* SCROLLBAR iOS */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1c1c1e;
    }
    ::-webkit-scrollbar-thumb {
        background: #ff3b30;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ff453a;
    }

    /* MENSAJES ERROR/SUCCESS iOS */
    .stSuccess, .stError {
        background: #1c1c1e !important;
        border: 1px solid #ff3b30 !important;
        border-radius: 12px !important;
        color: #ff3b30 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 16px !important;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .ruth-header {
            font-size: 36px !important;
            letter-spacing: 6px !important;
            margin: 24px 0 8px 0 !important;
        }
        .ruth-subtitle {
            font-size: 9px !important;
            letter-spacing: 2px !important;
        }
        .stButton>button {
            padding: 14px 12px !important;
            font-size: 12px !important;
        }
        [data-testid="stSidebar"] {
            width: 85vw !important;
        }
        [data-testid="stChatMessage"] {
            padding: 16px !important;
        }
    }
    
    @media (max-width: 480px) {
        .ruth-header {
            font-size: 28px !important;
            letter-spacing: 4px !important;
        }
        .stButton>button {
            padding: 12px 8px !important;
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
    st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>', unsafe_allow_html=True)
    
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
                    st.success("Cuenta creada")
                    time.sleep(1)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                except:
                    st.error("Usuario existente")
            
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
    
    esp_act = st.selectbox("Especialidad", list(ESP.keys()), key="esp_select")
    ton_act = st.selectbox("Personalidad", list(TON.keys()), key="ton_select")
    
    st.divider()
    
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(6).execute()
        if res.data:
            st.markdown("<p style='color: #8e8e93; font-size: 13px; font-weight: 500; letter-spacing: 0.5px; margin-bottom: 12px;'>HISTORIAL</p>", unsafe_allow_html=True)
            
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
