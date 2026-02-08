import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time
import urllib.parse

# --- FUNCIÓN PARA DETECTAR Y GENERAR IMÁGENES ---
def detectar_pedido_imagen(texto):
    """Detecta si el usuario pide generar una imagen"""
    palabras_clave = [
        'genera una imagen', 'crea una imagen', 'genera un', 'crea un',
        'muéstrame', 'dibuja', 'diseña', 'imagen de', 'foto de',
        'logo de', 'ilustra', 'render', 'visualiza'
    ]
    texto_lower = texto.lower()
    return any(palabra in texto_lower for palabra in palabras_clave)

def generar_imagen(prompt_texto):
    """
    Genera una URL de imagen usando Pollinations.ai (GRATIS)
    No requiere API key, es completamente gratuito
    """
    # Limpiar el prompt (quitar palabras de comando)
    prompt_limpio = prompt_texto.lower()
    for palabra in ['genera una imagen de', 'crea una imagen de', 'genera un', 'crea un', 
                    'muéstrame', 'dibuja', 'diseña', 'imagen de', 'foto de', 'logo de']:
        prompt_limpio = prompt_limpio.replace(palabra, '')
    
    prompt_limpio = prompt_limpio.strip()
    
    # Codificar el prompt para URL
    prompt_encoded = urllib.parse.quote(prompt_limpio)
    
    # URL de Pollinations.ai (GRATIS, sin API key)
    imagen_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"
    
    return imagen_url, prompt_limpio

# --- 1. CONFIGURACIÓN Y ESTÉTICA REFINADA ---
st.set_page_config(page_title="RUTH", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* FUENTES ULTRA FINAS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* FONDO NEGRO CON PATRÓN SUTIL */
    .stApp {
        background-color: #000000 !important;
        background-image: 
            repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255, 255, 255, 0.03) 2px, rgba(255, 255, 255, 0.03) 4px),
            repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255, 255, 255, 0.03) 2px, rgba(255, 255, 255, 0.03) 4px),
            radial-gradient(circle at 20% 30%, rgba(40, 40, 40, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(30, 30, 30, 0.4) 0%, transparent 50%);
        color: #ffffff !important;
    }
    
    /* FLECHA VISUAL REAL */
    [data-testid="stSidebarCollapsedControl"] {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%) !important;
        border: none !important;
        border-radius: 0 6px 6px 0 !important;
        width: 36px !important;
        height: 36px !important;
        top: 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3) !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: linear-gradient(135deg, #ff3333 0%, #ff0000 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.5) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* SIDEBAR GLASSMORPHISM */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.85) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 0, 0, 0.2) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #ff0000 !important;
        font-weight: 200 !important;
        letter-spacing: 0.4rem !important;
        text-align: center !important;
        margin: 2rem 0 1.5rem 0 !important;
        font-size: 1.1rem !important;
    }

    /* SELECTORES GLASS */
    [data-testid="stSidebar"] .stSelectbox label {
        color: #888 !important;
        font-size: 0.6rem !important;
        font-weight: 300 !important;
        letter-spacing: 0.15rem !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: #fff !important;
        padding: 0.7rem !important;
        font-size: 0.75rem !important;
        font-weight: 300 !important;
    }

    /* MENSAJES GLASS */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-left: 2px solid #ff0000 !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-left-color: #ff3333 !important;
        transform: translateX(4px) !important;
    }

    /* TÍTULO NEÓN */
    @keyframes neon-flicker {
        0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {
            opacity: 1;
            text-shadow: 
                0 0 10px rgba(255, 0, 0, 0.8),
                0 0 20px rgba(255, 0, 0, 0.6),
                0 0 40px rgba(255, 0, 0, 0.4);
        }
        20%, 21.999%, 63%, 63.999%, 65%, 69.999% {
            opacity: 0.3;
            text-shadow: none;
        }
    }
    
    .ruth-header {
        text-align: center;
        color: #ff0000;
        font-size: clamp(2.5rem, 8vw, 5rem);
        font-weight: 100 !important;
        letter-spacing: clamp(0.8rem, 3vw, 2rem);
        margin: clamp(1.5rem, 5vh, 3rem) 0 clamp(0.5rem, 2vh, 1rem) 0;
        animation: neon-flicker 5s infinite;
    }
    
    .ruth-subtitle {
        text-align: center;
        color: #666;
        font-size: clamp(0.5rem, 1.2vw, 0.65rem);
        font-weight: 200 !important;
        letter-spacing: clamp(0.3rem, 1vw, 0.5rem);
        margin-bottom: clamp(2rem, 5vh, 3rem);
        text-transform: uppercase;
    }

    /* BOTONES GLASS */
    .stButton>button {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #999 !important;
        padding: clamp(1rem, 2.5vw, 1.2rem) clamp(0.6rem, 2vw, 0.8rem) !important;
        font-size: clamp(0.55rem, 1.5vw, 0.7rem) !important;
        font-weight: 300 !important;
        letter-spacing: 0.2rem !important;
        text-transform: uppercase !important;
        transition: all 0.4s ease !important;
        width: 100% !important;
    }
    
    .stButton>button:hover {
        background: rgba(255, 0, 0, 0.05) !important;
        border-color: rgba(255, 0, 0, 0.3) !important;
        color: #ff0000 !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="stSidebar"] .stButton>button {
        padding: 0.8rem !important;
        font-size: 0.65rem !important;
        margin: 0.4rem 0 !important;
    }
    
    .delete-history-btn button {
        background: rgba(255, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 0, 0, 0.3) !important;
        color: #ff0000 !important;
    }

    /* INPUT CHAT */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: white !important;
        font-size: clamp(0.85rem, 2vw, 0.95rem) !important;
        font-weight: 300 !important;
    }

    /* LOGIN */
    div[data-testid="stTextInput"] input {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #fff !important;
        padding: 1.2rem !important;
        text-align: center !important;
        font-weight: 300 !important;
        letter-spacing: 0.2rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255, 0, 0, 0.4) !important;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    /* IMAGEN GENERADA - ESTILO GLASS */
    .generated-image {
        border: 2px solid rgba(255, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(255, 0, 0, 0.2) !important;
        margin: 1rem 0 !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.3), transparent) !important;
        margin: clamp(1.5rem, 4vh, 2.5rem) 0 !important;
    }

    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.02); }
    ::-webkit-scrollbar-thumb { background: rgba(255, 0, 0, 0.4); border-radius: 3px; }

    @media (max-width: 768px) {
        .ruth-header { font-size: 2.2rem !important; letter-spacing: 0.6rem !important; }
        .ruth-subtitle { font-size: 0.45rem !important; }
        .stButton>button { padding: 1rem 0.5rem !important; font-size: 0.55rem !important; }
        [data-testid="stSidebar"] { width: 85vw !important; }
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
    
    col_l, col_c, col_r = st.columns([0.25, 2, 0.25])
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
                    st.error("Acceso denegado")
            
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
                    st.success("Cuenta creada")
                    time.sleep(1)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                except:
                    st.error("Usuario existente")
            
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
            st.markdown("<p style='color: #888; font-size: 0.6rem; font-weight: 300; letter-spacing: 0.1rem;'>HISTORIAL</p>", unsafe_allow_html=True)
            
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
                tit = chat['messages'][0]['content'][:16].upper() if chat['messages'] else "VACÍO"
                if st.button(f"{tit}...", key=chat['id']):
                    st.session_state.messages = chat['messages']
                    st.rerun()
    except:
        pass

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE + IA VISUAL</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Grid responsive
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

# Chat con soporte de imágenes
for msg in st.session_state.messages:
    if "Ejecuta:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            # Si el mensaje contiene una URL de imagen, mostrarla
            if msg["role"] == "assistant" and "![IMAGEN](" in msg["content"]:
                partes = msg["content"].split("![IMAGEN](")
                st.markdown(partes[0])
                url_imagen = partes[1].split(")")[0]
                st.markdown(f'<img src="{url_imagen}" class="generated-image" style="width: 100%; max-width: 600px; border-radius: 12px;">', unsafe_allow_html=True)
                if len(partes[1].split(")")) > 1:
                    st.markdown(partes[1].split(")", 1)[1])
            else:
                st.markdown(msg["content"])

if prompt := st.chat_input("Mensaje (prueba: 'genera una imagen de un gato cyberpunk')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=ruth_avatar):
        # DETECTAR SI PIDE IMAGEN
        if detectar_pedido_imagen(prompt):
            # Generar imagen
            imagen_url, prompt_limpio = generar_imagen(prompt)
            
            # Respuesta de RUTH + imagen
            respuesta = f"✨ Imagen generada: **{prompt_limpio}**\n\n![IMAGEN]({imagen_url})\n\n*Generado con IA visual de RUTH*"
            
            st.markdown(f"✨ Imagen generada: **{prompt_limpio}**")
            st.markdown(f'<img src="{imagen_url}" class="generated-image" style="width: 100%; max-width: 600px; border-radius: 12px;">', unsafe_allow_html=True)
            st.markdown("*Generado con IA visual de RUTH*")
            
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        else:
            # Respuesta normal de texto
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
```
