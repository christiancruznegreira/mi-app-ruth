import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA GLOW ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide")

st.markdown("""
    <style>
    /* Fondo con Patrón Unificado */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }

    /* Branding RUTH */
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0; text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.3);}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}

    /* Botones ROJOS con BRILLO (Glow) */
    .stButton>button {
        border-radius: 10px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        transition: 0.4s;
        font-weight: 200 !important;
        letter-spacing: 0.1rem;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important;
        color: white !important;
    }

    /* Estilo del Chat */
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES ---
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

if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. CENTRO DE MANDO (SIDEBAR PLEGABLE) ---
with st.sidebar:
    st.markdown("<h3 style='color: white; font-weight: 200; letter-spacing: 0.3rem;'>COMMAND CENTER</h3>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Especialidad de RUTH:", ["Legal", "Amazon FBA", "Marketing", "Estrategia"])
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem; letter-spacing: 0.1rem;'>HISTORIAL DE CHAT</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    if not historial:
        st.caption("No hay chats en la nube.")
    for chat in historial:
        fecha = chat['created_at'][11:16]
        if st.button(f"📜 Chat {fecha}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 4. INTERFAZ PRINCIPAL (BOTONES RÁPIDOS) ---
col1, col2, col3, col4 = st.columns(4)
prompts_r = {"Email": "Redacta un email profesional.", "Legal": "Revisa esta cláusula.", "Amazon": "Optimiza SEO Amazon.", "Idea": "Dame una idea disruptiva."}

def enviar(t):
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(messages=[{"role":"system","content":f"Eres RUTH {modo}"}]+st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

with col1: 
    if st.button("📝 Email"): enviar(prompts_r["Email"]); st.rerun()
with col2: 
    if st.button("⚖️ Legal"): enviar(prompts_r["Legal"]); st.rerun()
with col3: 
    if st.button("📦 Amazon"): enviar(prompts_r["Amazon"]); st.rerun()
with col4: 
    if st.button("💡 Idea"): enviar(prompts_r["Idea"]); st.rerun()

st.divider()

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

if prompt := st.chat_input("Consulta a RUTH Professional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content":f"Eres RUTH {modo}"}]+st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
