import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (INTACTA) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; opacity: 1; }
        50% { color: #660000; text-shadow: none; opacity: 0.8; }
    }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    [data-testid="column"] { padding: 0px 1px !important; text-align: center !important; }
    .stButton>button {
        border: none !important;
        background-color: transparent !important;
        color: #aaaaaa !important; 
        width: 100% !important;
        height: 40px !important;
        transition: 0.2s ease;
        text-transform: uppercase;
        font-size: 0.52rem !important; 
        font-weight: 400 !important;
        letter-spacing: 0.02rem !important;
        white-space: nowrap !important;
        overflow: visible !important;
        cursor: pointer;
        display: block !important;
    }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; background-color: transparent !important; border: none !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. PERSONALIDADES Y CONEXIONES ---
PERSONALIDADES = {
    "Abogada": "Eres RUTH Legal Advisor. Tono formal, jurídico y técnico.",
    "Amazon Pro": "Eres RUTH Amazon Strategist. SEO, ventas y rentabilidad.",
    "Marketing": "Eres RUTH Creative Copywriter. Persuasiva y vibrante.",
    "Estratega": "Eres RUTH CEO Consultant. Escalabilidad y visión ejecutiva.",
    "Médico": "Eres RUTH Medical Specialist. Científica y empática.",
    "Estudiante": "Eres RUTH Tutor Académico. Didáctica y paciente.",
    "Anime": "Eres RUTH Otaku Sensei. Experta en anime y cultura japonesa."
}

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. FUNCIONES DE LÓGICA ADAPTATIVA ---
def procesar_comando_inteligente(etiqueta, modo_actual):
    # Diccionario que adapta la orden según QUIÉN es RUTH en ese momento
    prompt_base = {
        "CORREO": f"Como experta en {modo_actual}, redacta un correo profesional impecable sobre este tema: ",
        "LEGAL": f"Analiza este caso jurídico desde tu perspectiva de {modo_actual}: ",
        "AMAZON": f"Aplica tus conocimientos de {modo_actual} para optimizar un listado de Amazon paso a paso.",
        "ESTRATEGIA": f"Desde tu visión de {modo_actual}, propón una estrategia de negocio disruptiva y escalable.",
        "SALUD": f"Como experta en {modo_actual}, explica un concepto de salud o bienestar de forma técnica.",
        "ESTUDIOS": f"Actúa como tutora en {modo_actual} y ayúdame a resumir o estudiar este concepto complejo.",
        "ANIME": f"Desde tu perspectiva de {modo_actual}, hazme una recomendación de anime que encaje con mis gustos."
    }
    
    orden_final = prompt_base.get(etiqueta, "Hola, ¿en qué puedes ayudarme?")
    
    st.session_state.messages.append({"role": "user", "content": orden_final})
    c = client.chat.completions.create(
        messages=[{"role":"system","content": PERSONALIDADES[modo_actual]}] + st.session_state.messages, 
        model="llama-3.3-70b-versatile"
    )
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    modo = st.selectbox("Especialidad:", list(PERSONALIDADES.keys()))
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            if st.button(f"📜 Chat {chat['created_at'][11:16]}", key=chat['id']):
                st.session_state.messages = chat['messages']
                st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL (BOTONES ADAPTATIVOS) ---
cols = st.columns(7)
labels = ["CORREO", "LEGAL", "AMAZON", "ESTRATEGIA", "SALUD", "ESTUDIOS", "ANIME"]

for i in range(7):
    with cols[i]:
        if st.button(labels[i]): 
            procesar_comando_inteligente(labels[i], modo)
            st.rerun()

st.divider()

# --- 6. CHAT ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Hablando con RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
