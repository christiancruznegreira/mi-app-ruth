import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA MINIMALISTA ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    
    /* Neón Rojo Roto */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    /* REJILLA DE 8 BOTONES GHOST */
    [data-testid="column"] { padding: 0px 1px !important; text-align: center !important; }
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
        letter-spacing: 0.01rem !important;
        white-space: nowrap !important;
        cursor: pointer;
    }
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; opacity: 1; }
        50% { color: #660000; text-shadow: none; opacity: 0.8; }
    }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; background-color: transparent !important; }
    
    /* Botón PDF Especial */
    .pdf-btn button {
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
        font-size: 0.7rem !important;
    }

    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE PDF ---
def generar_pdf_bytes(mensajes, modo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "RUTH - PROFESSIONAL REPORT", ln=True, align="C")
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

# --- 3. CONEXIONES Y PERSONALIDADES ---
PERSONALIDADES = {
    "Abogada": "Eres RUTH Legal Advisor. Tono formal y técnico.",
    "Amazon Pro": "Eres RUTH Amazon Strategist. SEO y ventas.",
    "Marketing": "Eres RUTH Copywriter Pro. Persuasiva.",
    "Estratega": "Eres RUTH CEO Advisor. Visión ejecutiva.",
    "Médico": "Eres RUTH Médico. Científica y rigurosa.",
    "Finanzas": "Eres RUTH Wealth Manager. Análisis de riesgos.",
    "IA Pro": "Eres RUTH AI Architect. Automatización.",
    "Seguridad": "Eres RUTH Cybersecurity Lead. Protección."
}

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def guardar_nube(mensajes):
    if mensajes:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
        except: pass

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL (CENTRO DE MANDO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    # BOTÓN PDF SIEMPRE VISIBLE
    st.divider()
    st.markdown("### EXPORTAR")
    try:
        # Si no hay mensajes, enviamos una lista vacía para que el botón no rompa
        msjs_pdf = st.session_state.messages if st.session_state.messages else [{"role":"system", "content":"Documento vacío"}]
        pdf_data = generar_pdf_bytes(msjs_pdf, "Reporte")
        st.download_button(label="DESCARGAR PDF", data=pdf_data, file_name="RUTH_Reporte.pdf", mime="application/pdf", help="Descargar conversación actual")
    except:
        st.caption("Preparando motor PDF...")

    st.divider()
    modo = st.selectbox("Especialidad:", list(PERSONALIDADES.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL DE SESIONES</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(8).execute()
        for chat in res.data:
            # EXTRAER TÍTULO INTELIGENTE (Primeras palabras del primer mensaje de usuario)
            msg_usuario = "Sin contenido"
            for m in chat['messages']:
                if m['role'] == 'user':
                    msg_usuario = m['content'][:25].upper() + "..."
                    break
            
            fecha = chat['created_at'][11:16]
            # Botón sin emoji, solo texto minimalista
            if st.button(f"{msg_usuario} ({fecha})", key=chat['id']):
                st.session_state.messages = chat['messages']
                st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL (8 BOTONES) ---
def enviar_c(etiqueta, modo_actual):
    prompts_base = {"LEGAL": "Análisis legal:", "AMAZON": "Optimización Amazon:", "MARKETING": "Campaña creativa:", "ESTRATEGIA": "Plan estratégico:", "SALUD": "Consulta médica:", "FINANZAS": "Análisis financiero:", "IA PRO": "Automatización IA:", "SEGURIDAD": "Auditoría seguridad:"}
    st.session_state.messages.append({"role": "user", "content": prompts_base.get(etiqueta, "Consulta profesional")})
    c = client.chat.completions.create(messages=[{"role":"system","content": PERSONALIDADES[modo_actual]}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8)
labels = ["LEGAL", "AMAZON", "MARKETING", "ESTRATEGIA", "SALUD", "FINANZAS", "IA PRO", "SEGURIDAD"]
for i in range(8):
    with cols[i]:
        if st.button(labels[i]): enviar_c(labels[i], modo); st.rerun()

st.divider()

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
