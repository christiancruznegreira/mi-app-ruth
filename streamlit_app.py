import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (BARRA LATERAL PROTEGIDA) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE (FIJA Y ROJA) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 0px 10px 10px 0px;
        left: 0px !important;
        top: 20px !important;
        padding: 8px !important;
        display: flex !important;
    }

    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
    footer { visibility: hidden; }

    /* Título Neón Rojo */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    /* BOTONES GHOST (INCLUIDO PDF) */
    [data-testid="column"] { padding: 0px 1px !important; }
    .stButton>button {
        border: none !important;
        background-color: transparent !important;
        color: #aaaaaa !important; 
        width: 100% !important;
        height: 40px !important;
        transition: 0.2s ease;
        text-transform: uppercase;
        font-size: 0.48rem !important; 
        font-weight: 400 !important;
        white-space: nowrap !important;
        cursor: pointer;
    }
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; opacity: 1; }
        50% { color: #660000; text-shadow: none; opacity: 0.8; }
    }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; background-color: transparent !important; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIOS ---
ESPECIALIDADES = {
    "Abogada": "como Abogada Senior de Élite.",
    "Amazon Pro": "como Especialista en Amazon FBA.",
    "Marketing": "como Directora de Marketing Pro.",
    "Estratega": "como CEO Advisor Estratégico.",
    "Médico": "como Médico Especialista.",
    "Finanzas": "como Analista de Inversiones.",
    "IA Pro": "como Arquitecto de IA.",
    "Seguridad": "como Experto en Ciberseguridad."
}

TONOS = {
    "Sarcástica": "Tono cínico, mordaz e inteligente. Te burlas sutilmente y eres cortante.",
    "Empática": "Tono suave, paciente y enfocado en el apoyo emocional incondicional.",
    "Analítica": "Tono puramente lógico, frío, basado solo en datos y hechos crudos.",
    "Motivadora": "Tono enérgico, inspirador y agresivamente positivo hacia el éxito.",
    "Ejecutiva": "Tono sobrio, breve y enfocado exclusivamente en el ROI.",
    "Conspiranoica": "Tono suspicaz, buscas patrones de control ocultos en todo."
}

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def generar_pdf_bytes(mensajes, esp):
    pdf = FPDF()
    pdf.add_page(); pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"RUTH REPORT - {esp.upper()}", ln=True, align="C"); pdf.ln(10)
    for msg in mensajes:
        rol = "USER" if msg["role"] == "user" else "RUTH"
        pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 8, f"{rol}:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        texto = msg["content"].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, texto); pdf.ln(4)
    return bytes(pdf.output())

def guardar_nube(mensajes):
    if mensajes:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
    except: pass

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    especialidad = st.selectbox("Especialidad:", list(ESPECIALIDADES.keys()))
    personalidad = st.selectbox("Personalidad:", list(TONOS.keys()))
    
    # Botón PDF Minimalista Ghost
    st.divider()
    if st.session_state.messages:
        try:
            pdf_data = generar_pdf_bytes(st.session_state.messages, especialidad)
            st.download_button(label="📥 EXPORTAR PDF", data=pdf_data, file_name="RUTH_Reporte.pdf", mime="application/pdf")
        except: st.caption("PDF Ready")

    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            m_u = chat['messages'][0]['content'][:20].upper()+"..." if chat['messages'] else "Vacío"
            if st.button(f"{m_u}", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. LOGICA DE IA (ACTITUD EN TIEMPO REAL) ---
def enviar_c(t):
    # Forzamos la personalidad en el prompt de sistema justo antes de enviar
    system_inst = f"Identidad TOTAL: {ESPECIALIDADES[especialidad]} Tono ABSOLUTO: {TONOS[personalidad]} PROHIBIDO disculparte. Actúa así ahora mismo."
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(messages=[{"role":"system","content": system_inst}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_c(f"Comando: {labels[i]}"); st.rerun()

st.divider()

# --- 6. CHAT LOOP ---
for msg in st.session_state.messages:
    if "Identidad TOTAL" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {especialidad} ({personalidad})"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        # Inyección de actitud forzada en cada mensaje
        system_inst = f"Identidad RUTH: {ESPECIALIDADES[especialidad]} Tono: {TONOS[personalidad]} PROHIBIDO disculparte. Sé radicalmente fiel a tu nueva personalidad."
        c = client.chat.completions.create(messages=[{"role":"system","content": system_inst}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
