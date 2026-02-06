import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. ESTÉTICA Y CONFIGURACIÓN ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    .stButton>button { border-radius: 20px !important; border: 1px solid #ff4b4b !important; background-color: transparent !important; color: white !important; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #ff4b4b !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES (GROQ Y SUPABASE) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def guardar_nube(mensajes):
    try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
    except: pass

def cargar_nube():
    try: 
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        return res.data
    except: return []

# --- 3. GESTIÓN DE MEMORIA Y ESTADOS ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL (WORKSPACE Y MODOS) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Especialidad:", ["Legal", "Amazon FBA", "Marketing", "Estrategia"])
    
    st.divider()
    st.markdown("### ☁️ HISTORIAL CLOUD")
    historial = cargar_nube()
    for chat in historial:
        if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 5. INTERFAZ PRINCIPAL (BOTONES RÁPIDOS) ---
col1, col2, col3, col4 = st.columns(4)
prompts_rapidos = {
    "Email": "RUTH, redacta un email profesional elegante.",
    "Legal": "RUTH, revisa la seguridad de esta cláusula legal.",
    "Amazon": "RUTH, optimiza el SEO de este producto para Amazon.",
    "Estrategia": "RUTH, propón una estrategia de negocio disruptiva."
}

def enviar_comando(texto):
    st.session_state.messages.append({"role": "user", "content": texto})
    # Llamada inmediata a la IA
    completion = client.chat.completions.create(
        messages=[{"role": "system", "content": f"Eres RUTH, experta en {modo}."}] + st.session_state.messages,
        model="llama-3.3-70b-versatile"
    )
    res = completion.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": res})

with col1: 
    if st.button("📝 Email"): enviar_comando(prompts_rapidos["Email"]); st.rerun()
with col2: 
    if st.button("⚖️ Legal"): enviar_comando(prompts_rapidos["Legal"]); st.rerun()
with col3: 
    if st.button("📦 Amazon"): enviar_comando(prompts_rapidos["Amazon"]); st.rerun()
with col4: 
    if st.button("💡 Estrategia"): enviar_comando(prompts_rapidos["Estrategia"]); st.rerun()

st.divider()

# --- 6. MOSTRAR CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

if prompt := st.chat_input("Consulta a RUTH Ultra..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": f"Eres RUTH, experta en {modo}."}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        res = completion.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
