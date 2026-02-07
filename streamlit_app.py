import streamlit as st
from groq import Groq
from supabase import create_client, Client
from PyPDF2 import PdfReader
import os
import datetime

# --- 1. ESTÉTICA PREMIUM (NEÓN Y PATRÓN) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0 10px 10px 0; left: 0; top: 15px; padding: 5px; display: flex; z-index: 999999;
    }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
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

# Función para leer PDF
def leer_pdf(archivos):
    texto = ""
    for a in archivos:
        try:
            r = PdfReader(a)
            for p in r.pages:
                texto += p.extract_text() + "\n"
        except: pass
    return texto

# --- 3. DICCIONARIOS ---
ESPECIALIDADES = {"Abogada": "Abogada Senior.", "Amazon Pro": "Especialista Amazon.", "Marketing": "Directora Marketing.", "Estratega": "CEO Advisor.", "Médico": "Médico.", "Finanzas": "Financiera.", "IA Pro": "Arquitecto IA.", "Seguridad": "Ciberseguridad."}
TONOS = {"Analítica": "Fría y lógica.", "Sarcástica": "Cínica e irónica.", "Empática": "Cálida y paciente.", "Motivadora": "Enérgica.", "Ejecutiva": "Directa al ROI.", "Conspiranoica": "Suspicaz."}

if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        st.session_state.messages = []; st.session_state.pdf_text = ""; st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #ff4b4b; font-size: 0.7rem; font-weight: bold;'>BASE DE CONOCIMIENTO</p>", unsafe_allow_html=True)
    pdf_upload = st.file_uploader("SUBIR PDF PARA ANALIZAR:", type=['pdf'], accept_multiple_files=True)
    
    if pdf_upload:
        st.session_state.pdf_text = leer_pdf(pdf_upload)
        # Mostrar cuánta información ha leído RUTH
        palabras = len(st.session_state.pdf_text.split())
        st.caption(f"✅ RUTH ha asimilado {palabras} palabras del documento.")

    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}"): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            # Inyectamos el PDF en el comando de los botones
            contexto = f"\nDOCUMENTO CARGADO: {st.session_state.pdf_text[:3000]}\n" if st.session_state.pdf_text else ""
            sys_inst = f"Eres RUTH {ESPECIALIDADES[esp_act]} ({TONOS[ton_act]}). {contexto} Realiza una acción de tu área."
            st.session_state.messages.append({"role": "user", "content": f"Acción: {labels[i]}"})
            c = client.chat.completions.create(messages=[{"role":"system","content": sys_inst}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
            st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content}); st.rerun()

st.divider()

for msg in st.session_state.messages:
    if "Acción:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        # EL SECRETO ESTÁ AQUÍ: Pasamos el PDF en cada respuesta
        contexto = f"\nESTE ES EL TEXTO DEL PDF QUE SUBIÓ EL USUARIO:\n'''{st.session_state.pdf_text[:4000]}'''\nUsa este texto para responder." if st.session_state.pdf_text else ""
        sys_i = f"Eres RUTH {esp_act} ({TONOS[ton_act]}). {contexto}"
        
        c = client.chat.completions.create(messages=[{"role":"system","content": sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
