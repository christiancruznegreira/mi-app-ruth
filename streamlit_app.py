import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN VISUAL ESTABLE ---
st.set_page_config(
    page_title="RUTH Pro", 
    page_icon="●", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Fondo Negro Premium con Patrón */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* Título RUTH Gigante Rojo */
    .ruth-header { 
        text-align: center; color: #ff4b4b; font-size: 5rem; 
        font-weight: 100; letter-spacing: 1.2rem; padding-top: 1rem;
        text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.3);
    }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}

    /* Botones con Glow */
    .stButton>button {
        border-radius: 12px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.5) !important;
    }

    /* Texto claro */
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES SEGURAS ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Error en Secrets. Verifica tus llaves en Streamlit.")
    st.stop()

# --- 3. EXPERTOS ---
EXPERTOS = {
    "Abogada": "Actúas como Abogada Senior. Sin disculpas. Rigor legal.",
    "Amazon Pro": "Actúas como Especialista en Amazon. SEO y ventas.",
    "Marketing": "Actúas como Directora Creativa. Persuasión.",
    "Estratega": "Actúas como Consultora CEO. Estrategia empresarial."
}

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL (CENTRO DE MANDO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Identidad de RUTH:", list(EXPERTOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
                st.session_state.messages = chat['messages']
                st.rerun()
    except:
        st.caption("Conectando con historial...")

# --- 5. CUERPO PRINCIPAL ---
# Botones rápidos
col1, col2, col3, col4 = st.columns(4)
with col1: 
    if st.button("📝 Email"): 
        st.session_state.messages.append({"role": "user", "content": "Redacta un correo profesional."})
        st.rerun()
# (Puedes añadir los otros 3 botones siguiendo el mismo formato si lo deseas)

st.divider()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consulta a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        c = client.chat.completions.create(
            messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
