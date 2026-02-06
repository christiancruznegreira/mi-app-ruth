import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (BARRA LATERAL Y BOTÓN PDF) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium Unificado */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE (FIJA Y ROJA) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0 10px 10px 0 !important; left: 0 !important;
        top: 20px !important; width: 50px !important; height: 40px !important;
        display: flex !important; justify-content: center !important; z-index: 999999 !important;
    }

    /* TÍTULO NEÓN ROJO */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; margin-bottom: 0px;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* BOTÓN PDF CIRCULAR FLOTANTE */
    .stDownloadButton { position: fixed; bottom: 32px; right: 80px; z-index: 1000; }
    .stDownloadButton > button {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 50% !important; width: 50px !important; height: 50px !important;
        border: none !important; font-weight: bold !important; font-size: 0.7rem !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.5) !important; transition: 0.3s;
    }
    .stDownloadButton > button:hover { transform: scale(1.1); }

    /* BOTONES GHOST MINIMALISTAS */
    [data-testid="column"] { padding: 0 1px !important; }
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    
    header, footer { visibility: hidden; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIOS DE INTELIGENCIA ---
ESPECIALIDADES = {
    "Abogada": "como Abogada Senior.", "Amazon Pro": "como Especialista en Amazon FBA.",
    "Marketing": "como Directora de Marketing.", "Estratega": "como CEO Advisor.",
    "Médico": "como Médico Especialista.", "Finanzas": "como Analista de Inversiones.",
    "IA Pro": "como Arquitecto de IA.", "Seguridad": "como Líder en Ciberseguridad."
}

TONOS = {
    "Sarcástica": "Tono cínico, mordaz e irónico.", "Empática": "Tono suave, cálido y paciente.",
    "Analítica": "Tono lógico, frío y basado en datos.", "Motivadora": "Tono enérgico e inspirador.",
    "Ejecutiva": "Tono sobrio y directo al ROI.", "Conspiranoica": "Tono suspicaz y detectivesco."
}

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def generar_pdf_seguro(mensajes, esp):
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"RUTH REPORT - {esp.upper()}", ln=True, align="C"); pdf.ln(10)
        for msg in mensajes:
            rol = "USER" if msg["role"] == "user" else "RUTH"
            pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 8, f"{rol}:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            t = msg["content"].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, t); pdf.ln(4)
        return bytes(pdf.output())
    except: return None

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL (WORKSPACE COMPLETO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            try: supabase.table("chats").insert({"user_email": "Invitado", "messages": st.session_state.messages}).execute()
            except: pass
        st.session_state.messages = []; st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    # SECCIÓN LIBROS DINÁMICA
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>BIBLIOTECA</p>", unsafe_allow_html=True)
    if st.button("RECOMENDAR LITERATURA"):
        sys_l = f"Ignora el pasado. Eres RUTH {ESPECIALIDADES[esp_act]} con {TONOS[ton_act]}. Recomienda 3 libros de TU área."
        c_l = client.chat.completions.create(messages=[{"role":"system","content":sys_l}], model="llama-3.1-8b-instant")
        st.session_state.messages.append({"role": "assistant", "content": c_l.choices[0].message.content})
        st.rerun()

    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}..."): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO Y CHAT ---
if st.session_state.messages:
    p_data = generar_pdf_seguro(st.session_state.messages, esp_act)
    if p_data: st.download_button(label="PDF", data=p_data, file_name="RUTH_Report.pdf", mime="application/pdf")

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            sys_i = f"Identidad: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}. Responde a: {labels[i]}"
            st.session_state.messages.append({"role": "user", "content": f"Acción: {labels[i]}"})
            c = client.chat.completions.create(messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
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
        sys_i = f"Identidad: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}. Olvida roles anteriores."
        c = client.chat.completions.create(messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
