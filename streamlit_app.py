import streamlit as st
from groq import Groq
from supabase import create_client, Client
from PyPDF2 import PdfReader
import os
import datetime

# --- 1. ESTÉTICA PREMIUM (PARTÍCULAS, NEÓN Y FLECHA) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* FONDO CINÉTICO */
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

    /* FLECHA DE RESCATE ROJA INMORTAL */
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

# --- 2. DICCIONARIOS DE INTELIGENCIA CRUZADA ---
ESPECIALIDADES = {
    "Abogada": "experta en Derecho y Consultoría Legal.",
    "Amazon Pro": "Especialista en Amazon FBA y algoritmos.",
    "Marketing": "Directora de Marketing y Copywriter Pro.",
    "Estratega": "CEO Advisor y Estratega de Negocios.",
    "Médico": "Médico Especialista con rigor científico.",
    "Finanzas": "Analista de Inversiones y Wealth Manager.",
    "IA Pro": "Arquitecto de IA y experto en automatización.",
    "Seguridad": "Líder en Ciberseguridad y Privacidad."
}

TONOS = {
    "Sarcástica": "Tu tono es inteligente pero mordaz, cínico y cortante. Te burlas de la mediocridad.",
    "Empática": "Tu tono es suave, protector, paciente y lleno de apoyo emocional cálido.",
    "Analítica": "Tu tono es frío, basado solo en datos crudos, lógica pura y hechos.",
    "Motivadora": "Tu tono es enérgico, inspirador y agresivamente positivo hacia el éxito.",
    "Ejecutiva": "Tu tono es de alto nivel CEO. Breve, directo al grano y enfocado en el ROI.",
    "Conspiranoica": "Tu tono es suspicaz. Buscas patrones de control ocultos detrás de cada dato."
}

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def extraer_pdf(archivos):
    texto = ""
    for a in archivos:
        try:
            r = PdfReader(a)
            for p in r.pages: texto += p.extract_text() + "\n"
        except: pass
    return texto

def guardar_nube(mensajes):
    if len(mensajes) > 1:
        try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
        except: pass

if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_data" not in st.session_state: st.session_state.pdf_data = ""

# --- 4. BARRA LATERAL (WORKSPACE) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        guardar_nube(st.session_state.messages)
        st.session_state.messages = []; st.session_state.pdf_data = ""; st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #ff4b4b; font-size: 0.7rem; font-weight: bold;'>BASE DE CONOCIMIENTO</p>", unsafe_allow_html=True)
    pdf_up = st.file_uploader("ASIMILAR PDF:", type=['pdf'], accept_multiple_files=True)
    if pdf_up:
        st.session_state.pdf_data = extraer_pdf(pdf_up)
        st.caption("✅ Conocimiento integrado.")

    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = "VACÍO"
            for m in chat['messages']:
                if m['role'] == 'user': tit = m['content'][:20].upper() + "..."; break
            if st.button(f"{tit}"): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. LOGICA DE IA (ACTITUD DINÁMICA) ---
def responder_ia(prompt_usuario, es_boton=False):
    contexto_pdf = f"\nUSA ESTE CONOCIMIENTO: {st.session_state.pdf_data[:3500]}" if st.session_state.pdf_data else ""
    sys_inst = f"Eres RUTH. Actúas como {ESPECIALIDADES[esp_act]} {TONOS[ton_act]} {contexto_pdf} PROHIBIDO disculparte. Actúa fiel a tu rol ahora."
    
    mensajes = [{"role": "system", "content": sys_inst}] + st.session_state.messages[-10:]
    
    c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes)
    return c.choices[0].message.content

# Botones superiores
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Acción experta como {labels[i]}"})
            res = responder_ia(f"Acción {labels[i]}", es_boton=True)
            st.session_state.messages.append({"role": "assistant", "content": res}); st.rerun()

st.divider()

# --- 6. CHAT LOOP ---
for msg in st.session_state.messages:
    if "Acción experta" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        respuesta = responder_ia(prompt)
        st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
