import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime
import time
import urllib.parse

# --- FUNCIONES ---
def detectar_pedido_imagen(texto):
    palabras_clave = ['genera una imagen', 'crea una imagen', 'genera un', 'crea un', 'muéstrame', 'dibuja', 'diseña', 'imagen de', 'foto de', 'logo de']
    return any(palabra in texto.lower() for palabra in palabras_clave)

def generar_imagen(prompt_texto):
    prompt_limpio = prompt_texto.lower()
    for palabra in ['genera una imagen de', 'crea una imagen de', 'genera un', 'crea un', 'muéstrame', 'dibuja', 'diseña', 'imagen de', 'foto de', 'logo de']:
        prompt_limpio = prompt_limpio.replace(palabra, '')
    prompt_limpio = prompt_limpio.strip()
    prompt_encoded = urllib.parse.quote(prompt_limpio)
    imagen_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"
    return imagen_url, prompt_limpio

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="RUTH", page_icon="●", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #1a0000 0%, #000000 50%, #001a1a 100%);
    background-attachment: fixed;
}

.stApp::before {
    content: '';
    position: fixed;
    width: 100%;
    height: 100%;
    background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 30px 30px;
    pointer-events: none;
}

[data-testid="stSidebarCollapsedControl"] {
    background: #ff3b30 !important;
    border-radius: 0 10px 10px 0 !important;
}

[data-testid="stSidebar"] {
    background: #1a1a1a !important;
    border-right: 1px solid #ff3b30 !important;
}

[data-testid="stSidebar"] h3 {
    color: #ff3b30 !important;
    text-align: center !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    margin: 30px 0 !important;
}

[data-testid="stSidebar"] label {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #2a2a2a !important;
    border: 1px solid #ff3b30 !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    color: #ffffff !important;
    font-weight: 500 !important;
}

[role="listbox"] {
    background-color: #2a2a2a !important;
    border: 1px solid #ff3b30 !important;
}

[role="option"] {
    color: #ffffff !important;
    background-color: #2a2a2a !important;
}

[role="option"]:hover {
    background-color: rgba(255, 59, 48, 0.2) !important;
    color: #ff3b30 !important;
}

[data-testid="stChatMessage"] {
    background: rgba(30, 30, 30, 0.8) !important;
    border: 1px solid #333 !important;
    border-left: 3px solid #ff3b30 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
}

[data-testid="stChatMessage"] p {
    color: #f0f0f0 !important;
    line-height: 1.6 !important;
}

.ruth-header {
    text-align: center;
    color: #ff3b30;
    font-size: clamp(40px, 8vw, 70px);
    font-weight: 700;
    letter-spacing: 15px;
    margin: 50px 0 10px 0;
    text-shadow: 0 0 20px rgba(255, 59, 48, 0.5);
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px #ff3b30, 0 0 20px #ff3b30; }
    to { text-shadow: 0 0 20px #ff3b30, 0 0 30px #ff3b30, 0 0 40px #ff3b30; }
}

.ruth-subtitle {
    text-align: center;
    color: #888;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 3px;
    margin-bottom: 40px;
    text-transform: uppercase;
}

.stButton button {
    background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%) !important;
    border: 1px solid #444 !important;
    border-radius: 10px !important;
    color: #e0e0e0 !important;
    padding: 15px 20px !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, #ff3b30 0%, #ff2d55 100%) !important;
    border-color: #ff3b30 !important;
    color: white !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(255, 59, 48, 0.4) !important;
}

[data-testid="stSidebar"] .stButton button {
    padding: 12px !important;
    font-size: 11px !important;
}

[data-testid="stChatInput"] {
    background: #1a1a1a !important;
    border: 1px solid #444 !important;
    border-radius: 20px !important;
}

[data-testid="stChatInput"] textarea {
    color: #f0f0f0 !important;
}

div[data-testid="stTextInput"] input {
    background: #2a2a2a !important;
    border: 1px solid #ff3b30 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    padding: 15px !important;
    text-align: center !important;
    font-weight: 500 !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #ff3b30 !important;
    box-shadow: 0 0 0 3px rgba(255, 59, 48, 0.2) !important;
}

div[data-testid="stTextInput"] label {
    display: none !important;
}

.generated-image {
    border: 2px solid #ff3b30 !important;
    border-radius: 12px !important;
    box-shadow: 0 5px 20px rgba(255, 59, 48, 0.3) !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #ff3b30, transparent) !important;
    opacity: 0.5 !important;
    margin: 30px 0 !important;
}

footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #1a1a1a;
}
::-webkit-scrollbar-thumb {
    background: #ff3b30;
    border-radius: 4px;
}

@media (max-width: 768px) {
    .ruth-header {
        font-size: 35px !important;
        letter-spacing: 8px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
ruth_avatar = None  # Cambiado de "●" a None para evitar error

# --- ESTADOS ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN ---
def login_ui():
    st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
    st.markdown('<div class="ruth-subtitle">Universal Business Suite · IA Visual</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.auth_mode == "login":
            usuario = st.text_input("Usuario", placeholder="Usuario", key="login_user")
            password = st.text_input("Contraseña", type="password", placeholder="Contraseña", key="login_pass")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("ENTRAR", use_container_width=True):
                    res = supabase.table("usuarios").select("*").eq("username", usuario).eq("password", password).execute()
                    if res.data:
                        st.session_state.logged_in = True
                        st.session_state.user_name = usuario
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
            
            with col_btn2:
                if st.button("CREAR CUENTA", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.rerun()
        
        else:
            nuevo_user = st.text_input("Nuevo Usuario", placeholder="Usuario", key="signup_user")
            nuevo_pass = st.text_input("Nueva Contraseña", type="password", placeholder="Contraseña", key="signup_pass")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("REGISTRAR", use_container_width=True):
                    try:
                        supabase.table("usuarios").insert({"username": nuevo_user, "password": nuevo_pass}).execute()
                        st.success("✅ Cuenta creada exitosamente")
                        time.sleep(1.5)
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    except:
                        st.error("❌ El usuario ya existe")
            
            with col_btn2:
                if st.button("VOLVER", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()

if not st.session_state.logged_in:
    login_ui()
    st.stop()

# --- SIDEBAR ---
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
        "Abogada": "Abogada especializada en derecho corporativo.",
        "Amazon": "Experta en venta en Amazon y e-commerce.",
        "Marketing": "Especialista en marketing digital y estrategia.",
        "Estratega": "CEO Advisor y consultor estratégico.",
        "Médico": "Médico general con amplio conocimiento.",
        "Finanzas": "Experto en finanzas y inversiones.",
        "IA": "Especialista en inteligencia artificial.",
        "Seguridad": "Experto en ciberseguridad."
    }
    
    TON = {
        "Analítica": "Tono analítico y preciso.",
        "Sarcástica": "Tono sarcástico y directo.",
        "Empática": "Tono empático y comprensivo.",
        "Motivadora": "Tono motivador y energético.",
        "Ejecutiva": "Tono ejecutivo enfocado en ROI.",
        "Conspiranoica": "Tono conspirativo y profundo."
    }
    
    especialidad = st.selectbox("Especialidad", list(ESP.keys()), key="esp")
    personalidad = st.selectbox("Personalidad", list(TON.keys()), key="pers")
    
    st.divider()
    
    # Historial
    try:
        res = supabase.table("chats").select("*").eq("user_email", st.session_state.user_name).order("created_at", desc=True).limit(5).execute()
        if res.data:
            st.markdown("**HISTORIAL**")
            if st.button("🗑️ Borrar Todo", use_container_width=True):
                supabase.table("chats").delete().eq("user_email", st.session_state.user_name).execute()
                st.success("Historial borrado")
                time.sleep(1)
                st.rerun()
            
            for chat in res.data:
                titulo = chat['messages'][0]['content'][:20] if chat['messages'] else "Chat"
                if st.button(f"💬 {titulo}...", key=chat['id'], use_container_width=True):
                    st.session_state.messages = chat['messages']
                    st.rerun()
    except:
        pass

# --- MAIN ---
st.markdown('<div class="ruth-header">RUTH</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">Universal Business Suite · IA Visual</div>', unsafe_allow_html=True)

# Botones especialidades
cols = st.columns(4)
for i, label in enumerate(list(ESP.keys())):
    with cols[i % 4]:
        if st.button(label.upper(), key=f"btn_{i}"):
            st.session_state.messages.append({"role": "user", "content": f"Activa modo: {label}"})
            sys_prompt = f"Eres RUTH, {ESP[label]} {TON[personalidad]}"
            c = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-5:]
            )
            st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
            try:
                supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
            except:
                pass
            st.rerun()

st.divider()

# Mostrar mensajes
for msg in st.session_state.messages:
    if "Activa modo:" not in msg["content"]:
        avatar_to_use = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_to_use):
            if msg["role"] == "assistant" and "![IMAGEN](" in msg["content"]:
                partes = msg["content"].split("![IMAGEN](")
                st.markdown(partes[0])
                url = partes[1].split(")")[0]
                st.markdown(f'<img src="{url}" class="generated-image" style="width:100%; max-width:600px; border-radius:12px;">', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Escribe tu mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        if detectar_pedido_imagen(prompt):
            url, desc = generar_imagen(prompt)
            respuesta = f"✨ Imagen generada: **{desc}**\n\n![IMAGEN]({url})\n\n*Generado con IA de RUTH*"
            st.markdown(f"✨ Imagen generada: **{desc}**")
            st.markdown(f'<img src="{url}" class="generated-image" style="width:100%; max-width:600px; border-radius:12px;">', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        else:
            sys_prompt = f"Eres RUTH, {ESP[especialidad]} {TON[personalidad]}"
            c = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-5:],
                model="llama-3.3-70b-versatile"
            )
            res = c.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
        
        try:
            supabase.table("chats").insert({"user_email": st.session_state.user_name, "messages": st.session_state.messages}).execute()
        except:
            pass
