import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA ULTRA-MINIMALISTA ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }

    /* Animación de Parpadeo Rojo para el Hover */
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 10px #ff0000; opacity: 1; }
        50% { color: #880000; text-shadow: none; opacity: 0.7; }
    }

    /* Título Neón Rojo */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* BOTONES TIPO TEXTO (SIN RECUADRO) */
    .stButton>button {
        border: none !important;
        background-color: transparent !important;
        color: #888 !important; /* Texto gris por defecto */
        width: 100% !important;
        height: 40px !important;
        transition: 0.3s ease;
        text-transform: uppercase;
        font-size: 0.6rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.1rem;
        cursor: pointer;
    }
    
    /* Efecto al pasar el ratón */
    .stButton>button:hover {
        animation: text-flicker 0.5s infinite; /* Parpadeo rápido al señalar */
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. LOGICA DE PDF ---
def generar_pdf_bytes(mensajes, modo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "REPORTE PROFESIONAL - RUTH", ln=True, align="C")
    pdf.ln(10)
    for msg in mensajes:
        rol = "USUARIO" if msg["role"] == "user" else "RUTH"
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, f"{rol}:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        texto = msg["content"].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, texto)
        pdf.ln(4)
    return bytes(pdf.output())

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

PERSONALIDADES = {
    "Abogada": "Eres RUTH Legal Advisor. Tono formal.",
    "Amazon Pro": "Eres RUTH Amazon Strategist. SEO y ventas.",
    "Marketing": "Eres RUTH Copywriter. Persuasiva.",
    "Estratega": "Eres RUTH CEO Advisor. Visión ejecutiva.",
    "Médico": "Eres RUTH Médico. Científica.",
    "Estudiante": "Eres RUTH Tutor Académico. Didáctica.",
    "Anime": "Eres RUTH Otaku Sensei. Cultura japonesa."
}

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
    
    if st.session_state.messages:
        st.divider()
        try:
            pdf_data = generar_pdf_bytes(st.session_state.messages, "Global")
            st.download_button(label="📥 EXPORTAR PDF", data=pdf_data, file_name="RUTH_Reporte.pdf", mime="application/pdf")
        except: pass

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

# --- 5. CUERPO (7 BOTONES TIPO GHOST) ---
def enviar_c(t):
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(7)
labels = ["CORREO", "LEGAL", "AMAZON", "ESTRATEGIA", "SALUD", "ESTUDIOS", "ANIME"]
prompts = ["Redacta un correo.", "Análisis legal.", "SEO Amazon.", "Estrategia.", "Tema salud.", "Ayúdame a estudiar.", "Recomienda anime."]

for i in range(7):
    with cols[i]:
        if st.button(labels[i]): enviar_c(prompts[i]); st.rerun()

st.divider()

# --- 6. CHAT ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
