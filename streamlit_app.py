import streamlit as st
from groq import Groq
from supabase import create_client, Client
from PyPDF2 import PdfReader
import os
import datetime
import uuid

# --- 1. ESTÉTICA PREMIUM (PARTÍCULAS Y NEÓN) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 75, 75, 0.05) 0%, transparent 25%),
            radial-gradient(circle at 80% 70%, rgba(255, 75, 75, 0.05) 0%, transparent 25%),
            radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 30px 30px !important;
        animation: drift 15s infinite alternate ease-in-out;
    }
    @keyframes drift { from { background-position: 0% 0%; } to { background-position: 5% 5%; } }

    /* FLECHA DE RESCATE FIJA */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0 10px 10px 0 !important; left: 0 !important;
        top: 20px !important; width: 50px !important; height: 45px !important;
        display: flex !important; justify-content: center !important; 
        align-items: center !important; z-index: 999999 !important;
    }

    /* TÍTULO NEÓN ROJO */
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; margin-bottom: 0;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    /* BOTONES GHOST */
    [data-testid="column"] { padding: 0px 1px !important; }
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    
    header, footer { visibility: hidden; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE SESIÓN Y CONEXIONES ---
if "messages" not in st.session_state: st.session_state.messages = []
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())
if "pdf_data" not in st.session_state: st.session_state.pdf_data = ""

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def guardar_progreso():
    """Guarda o actualiza la conversación actual en Supabase."""
    if len(st.session_state.messages) > 1:
        try:
            data = {
                "user_email": "Invitado",
                "messages": st.session_state.messages,
                "session_id": st.session_state.session_id,
                "updated_at": datetime.datetime.now().isoformat()
            }
            # Usamos upsert para que si el session_id ya existe, se actualice en lugar de crear uno nuevo
            supabase.table("chats").upsert(data, on_conflict="session_id").execute()
        except: pass

def extraer_pdf(archivos):
    texto = ""
    for a in archivos:
        try:
            r = PdfReader(a)
            for p in r.pages: texto += p.extract_text() + "\n"
        except: pass
    return texto

# --- 3. DICCIONARIOS ---
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
    "Analítica": "Tono lógico, frío y basado en datos.",
    "Sarcástica": "Tono cínico, mordaz e inteligente.",
    "Empática": "Tono suave, paciente y empático.",
    "Motivadora": "Tono enérgico e inspirador.",
    "Ejecutiva": "Tono sobrio y directo al ROI.",
    "Conspiranoica": "Tono suspicaz y detectivesco."
}

# --- 4. BARRA LATERAL (CONTROL CENTER) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    if st.button("NUEVA CONVERSACIÓN"):
        guardar_progreso()
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.pdf_data = ""
        st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    pdf_up = st.file_uploader("ASIMILAR PDF:", type=['pdf'], accept_multiple_files=True)
    if pdf_up:
        st.session_state.pdf_data = extraer_pdf(pdf_up)
        st.caption("✅ Conocimiento asimilado.")

    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL DE SESIONES</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("updated_at", desc=True).limit(10).execute()
        for chat in res.data:
            m_u = "NUEVA SESIÓN"
            for m in chat['messages']:
                if m['role'] == 'user': m_u = m['content'][:20].upper() + "..."; break
            if st.button(f"{m_u}", key=chat['session_id']):
                st.session_state.messages = chat['messages']
                st.session_state.session_id = chat['session_id']
                st.rerun()
    except: st.caption("Conectando con historial...")

# --- 5. LÓGICA DE IA (DINAMISMO REAL) ---
def procesar_ia(prompt_usuario):
    ctx_pdf = f"\nUSA ESTE DOC: {st.session_state.pdf_data[:3500]}" if st.session_state.pdf_data else ""
    sys_inst = f"Identidad RUTH: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}. {ctx_pdf} PROHIBIDO disculparte por cambiar de modo."
    
    mensajes_finales = [{"role": "system", "content": sys_inst}] + st.session_state.messages[-10:]
    
    c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes_finales)
    respuesta = c.choices[0].message.content
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    guardar_progreso() # GUARDADO AUTOMÁTICO TRAS CADA RESPUESTA
    st.rerun()

# Botones Ghost
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Ejecutar acción experta: {labels[i]}"})
            procesar_ia(f"Acción {labels[i]}")

st.divider()

# --- 6. CHAT LOOP ---
for msg in st.session_state.messages:
    if "Ejecutar acción" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    procesar_ia(prompt)
