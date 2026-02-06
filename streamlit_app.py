import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. ESTÉTICA PREMIUM (Mantenemos el Neón) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00, 0 0 80px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5.5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.5rem; margin-bottom: 0px;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -15px; margin-bottom: 3rem;}
    .stButton>button { border-radius: 12px !important; border: 1px solid #ff4b4b !important; background-color: rgba(255, 75, 75, 0.05) !important; color: white !important; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #ff4b4b !important; box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- 3. FUNCIONES DE NUBE (GUARDAR Y CARGAR) ---
def guardar_en_nube(mensajes):
    if mensajes: # Solo guarda si hay algo escrito
        try:
            supabase.table("chats").insert({
                "user_email": "Invitado",
                "messages": mensajes
            }).execute()
        except: pass

def cargar_de_nube():
    try: 
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        return res.data
    except: return []

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    # EL CAMBIO ESTÁ AQUÍ: Primero guarda, luego limpia
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            guardar_en_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modo = st.selectbox("Identidad de RUTH:", ["Abogada", "Amazon Pro", "Marketing", "Estratega"])
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    historial = cargar_de_nube()
    for chat in historial:
        if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 5. LÓGICA DE IA Y BOTONES ---
EXPERTOS = {"Abogada": "RUTH Abogada.", "Amazon Pro": "RUTH Amazon.", "Marketing": "RUTH Marketing.", "Estratega": "RUTH CEO."}

def enviar_rapido(texto):
    st.session_state.messages.append({"role": "user", "content": texto})
    c = client.chat.completions.create(messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

col1, col2, col3, col4 = st.columns(4)
with col1: 
    if st.button("📝 Email"): enviar_rapido("Redacta un email profesional."); st.rerun()
with col2: 
    if st.button("⚖️ Análisis"): enviar_rapido("Haz un análisis experto."); st.rerun()
with col3: 
    if st.button("📦 Amazon"): enviar_rapido("Optimiza SEO Amazon."); st.rerun()
with col4: 
    if st.button("💡 Idea"): enviar_rapido("Idea disruptiva."); st.rerun()

st.divider()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        c = client.chat.completions.create(messages=[{"role":"system","content": EXPERTOS[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        
