import streamlit as st
from groq import Groq
import os
import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide")

# 2. ESTÉTICA PREMIUM UNIFICADA (CSS)
st.markdown("""
    <style>
    /* Fondo con Patrón para TODA la aplicación */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
        color: white !important;
    }

    /* Ocultar elementos de Streamlit */
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden !important; }

    /* Título RUTH en ROJO */
    .ruth-header {
        text-align: center; padding-top: 2rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem; margin-bottom: 0px;
    }
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.8rem; 
        margin-top: -10px; letter-spacing: 0.3rem; margin-bottom: 3rem;
        font-weight: bold;
    }

    /* Botones de la barra lateral */
    .stButton>button {
        width: 100%;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* Estilo del chat y texto */
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    
    /* Input de texto */
    .stChatInput {
        background-color: #1a1d24 !important;
        border-radius: 15px !important;
        border: 1px solid #333 !important;
    }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# 3. INICIALIZACIÓN DE MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = {}

# 4. BARRA LATERAL (WORKSPACE)
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    # Botón: Nueva Conversación
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            # Guardamos el chat actual con la hora de hoy (6 de Feb)
            id_c = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.history[f"Chat {id_c}"] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<p style='color: #888; font-size: 0.7rem; letter-spacing: 0.1rem;'>HISTORIAL RECIENTE</p>", unsafe_allow_html=True)
    
    # Mostrar chats guardados
    for chat_id in reversed(list(st.session_state.history.keys())):
        if st.button(f"📜 {chat_id}"):
            st.session_state.messages = st.session_state.history[chat_id]
            st.rerun()

    st.divider()
    modulo = st.selectbox(
        "Modo de Inteligencia:",
        ["Amazon FBA", "Legal", "Marketing", "Estrategia"]
    )

# 5. LÓGICA DE IA (GROQ)
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Personalidades Élite
prompts = {
    "Amazon FBA": "Eres RUTH Amazon Experta. SEO y ventas son tu vida.",
    "Legal": "Eres RUTH Legal Assistant. Precisión y derecho.",
    "Marketing": "Eres RUTH Copywriter. Persuasión y creatividad.",
    "Estrategia": "Eres RUTH Business Strategist. Escalabilidad y visión."
}

# Mostrar mensajes del chat actual
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# Entrada de Usuario
if prompt := st.chat_input("¿En qué puede ayudarte RUTH hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            sys_msg = f"{prompts[modulo]} Responde con elegancia como RUTH."
            full_msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            completion = client.chat.completions.create(
                messages=full_msgs,
                model="llama-3.3-70b-versatile"
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
        except Exception as e:
            st.error(f"Error: {e}")
