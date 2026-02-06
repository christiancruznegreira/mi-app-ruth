import streamlit as st
from groq import Groq
import os
import datetime

# 1. CONFIGURACIÓN Y ESTÉTICA UNIFICADA
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide")

st.markdown("""
    <style>
    /* Fondo y Patrón para toda la App (Principal y Sidebar) */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* Quitar bordes y líneas de Streamlit */
    [data-testid="stSidebar"] { border-right: 1px solid rgba(255, 255, 255, 0.05); }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    /* Título RUTH */
    .ruth-header {
        text-align: center; padding-top: 1rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3rem; margin-bottom: 0px;
    }
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.8rem; 
        margin-top: -10px; letter-spacing: 0.2rem; margin-bottom: 2rem;
    }

    /* Botones Premium en el Sidebar */
    .stButton>button {
        width: 100%;
        background-color: rgba(255, 75, 75, 0.1) !important;
        color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* Estilo del chat */
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {} # Aquí guardaremos los chats pasados

# 3. PANEL LATERAL DESPLEGABLE (SIDEBAR)
with st.sidebar:
    st.markdown("<h3 style='color: white; font-weight: 200;'>WORKSPACE</h3>", unsafe_allow_html=True)
    
    # Botón: Nueva Conversación
    if st.button("＋ NUEVA CONVERSACIÓN"):
        # Guardar la actual antes de borrar si tiene mensajes
        if st.session_state.messages:
            id_chat = datetime.datetime.now().strftime("%d/%m %H:%M")
            st.session_state.chat_history[id_chat] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<p style='color: #888; font-size: 0.8rem;'>CONVERSACIONES GUARDADAS</p>", unsafe_allow_html=True)
    
    # Listado de conversaciones guardadas
    if not st.session_state.chat_history:
        st.caption("No hay chats guardados aún.")
    else:
        for fecha in sorted(st.session_state.chat_history.keys(), reverse=True):
            if st.button(f"💬 {fecha}"):
                st.session_state.messages = st.session_state.chat_history[fecha]
                st.rerun()

    st.divider()
    negocio = st.selectbox(
        "Módulo Activo:",
        ["Amazon FBA", "Legal", "Marketing", "Académico", "Estrategia"]
    )

# 4. LÓGICA DE IA (GROQ)
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Personalidades
personalidades = {
    "Amazon FBA": "Eres RUTH Amazon Experta.",
    "Legal": "Eres RUTH Legal Assistant.",
    "Marketing": "Eres RUTH Copywriter Pro.",
    "Académico": "Eres RUTH Tutora Académica.",
    "Estrategia": "Eres RUTH Business Strategist."
}

# Mostrar Chat
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# Entrada de Usuario
if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            sys_prompt = f"{personalidades[negocio]} Responde profesionalmente como RUTH."
            mensajes_ia = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            completion = client.chat.completions.create(messages=mensajes_ia, model="llama-3.3-70b-versatile")
            respuesta = completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error: {e}")
