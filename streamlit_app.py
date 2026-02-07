import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
from PyPDF2 import PdfReader
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (SISTEMA TOTAL RUTH) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo y Patrón */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE (FIJA Y ROJA) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0px 10px 10px 0px !important; left: 0px !important;
        top: 20px !important; width: 50px !important; height: 40px !important;
        display: flex !important; justify-content: center !important; z-index: 999999 !important;
    }

    /* TÍTULO NEÓN ROJO GIGANTE */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; margin-bottom: 0px;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* BOTONES GHOST MINIMALISTAS */
    [data-testid="column"] { padding: 0 1px !important; }
    .stButton>button {
        border: none !important; background-color: transparent !important; color: #aaaaaa !important; 
        width: 100% !important; height: 40px !important; transition: 0.2s ease;
        text-transform: uppercase; font-size: 0.48rem !important; font-weight: 400 !important;
        white-space: nowrap !important; cursor: pointer;
    }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    
    header, footer { visibility: hidden; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES Y FUNCIONES TÉCNICAS ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def extraer_texto_pdf(archivos):
    texto = ""
    for a in archivos:
        try:
            r = PdfReader(a)
            for p in r.pages: texto += p.extract_text() + "\n"
        except: pass
    return texto

def guardar_nube(mensajes):
    if mensajes:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
        except: pass

# --- 3. DICCIONARIOS DE INTELIGENCIA ---
ESPECIALIDADES = {
    "Abogada": "como Abogada Senior.", "Amazon Pro": "como Especialista en Amazon FBA.",
    "Marketing": "como Directora de Marketing.", "Estratega": "como CEO Advisor.",
    "Médico": "como Médico Especialista.", "Finanzas": "como Analista de Inversiones.",
    "IA Pro": "como Arquitecto de IA.", "Seguridad": "como Líder en Ciberseguridad."
}

TONOS = {
    "Analítica": "Tono lógico y frío.", "Sarcástica": "Tono cínico e inteligente.",
    "Empática": "Tono suave y paciente.", "Motivadora": "Tono inspirador y positivo.",
    "Ejecutiva": "Tono sobrio y directo al ROI.", "Conspiranoica": "Tono suspicaz y detectivesco."
}

if "messages" not in st.session_state: st.session_state.messages = []
if "docs_context" not in st.session_state: st.session_state.docs_context = ""

# --- 4. BARRA LATERAL (WORKSPACE COMPLETO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []; st.session_state.docs_context = ""; st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    # NUEVA SECCIÓN: EVOLUCIÓN RAG
    st.divider()
    st.markdown("<p style='color: #ff4b4b; font-size: 0.7rem; font-weight: bold;'>BASE DE CONOCIMIENTO</p>", unsafe_allow_html=True)
    archivos = st.file_uploader("SUBIR DATOS TÉCNICOS:", type=['pdf', 'txt'], accept_multiple_files=True)
    if archivos:
        st.session_state.docs_context = extraer_texto_pdf(archivos)
        st.caption("CONOCIMIENTO ASIMILADO.")

    # SECCIÓN LIBROS
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>BIBLIOTECA</p>", unsafe_allow_html=True)
    if st.button("RECOMENDAR LITERATURA"):
        sys_l = f"Ignora el pasado. Eres RUTH {ESPECIALIDADES[esp_act]} con {TONOS[ton_act]}. Recomienda 3 libros de TU área actual ({esp_act})."
        c_l = client.chat.completions.create(messages=[{"role":"system","content":sys_l}], model="llama-3.1-8b-instant")
        st.session_state.messages.append({"role": "assistant", "content": c_l.choices[0].message.content}); st.rerun()

    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = "VACÍO"
            for m in chat['messages']:
                if m['role'] == 'user': tit = m['content'][:15].upper() + "..."; break
            if st.button(f"{tit} ({chat['created_at'][11:16]})", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
def enviar_c(etiqueta):
    contexto = f"\nCONOCIMIENTO EXTRA:\n{st.session_state.docs_context[:4000]}" if st.session_state.docs_context else ""
    sys_i = f"Identidad TOTAL: {ESPECIALIDADES[esp_act]} Tono ABSOLUTO: {TONOS[ton_act]}. {contexto} Responde a: {etiqueta}"
    st.session_state.messages.append({"role": "user", "content": f"EJECUTAR: {etiqueta}"})
    c = client.chat.completions.create(messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_c(labels[i]); st.rerun()

st.divider()

for msg in st.session_state.messages:
    if "Identidad TOTAL" not in msg["content"] and "EJECUTAR:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        contexto = f"\nCONOCIMIENTO CARGADO:\n{st.session_state.docs_context[:4000]}" if st.session_state.docs_context else ""
        sys_i = f"Eres RUTH {esp_act} {ton_act}. {contexto} PROHIBIDO disculparte."
        c = client.chat.completions.create(messages=[{"role":"system","content": sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
