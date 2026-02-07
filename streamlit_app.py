import streamlit as st
from groq import Groq
from supabase import create_client, Client
from PyPDF2 import PdfReader
import base64
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (FLECHA Y BARRA FIJAS) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* FLECHA DE RESCATE (GARANTIZADA) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0px 10px 10px 0px !important; left: 0px !important;
        top: 20px !important; width: 50px !important; height: 40px !important;
        display: flex !important; justify-content: center !important; z-index: 999999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg { fill: white !important; }

    /* Estética Visual */
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    
    /* BOTONES GHOST */
    [data-testid="column"] { padding: 0px 1px !important; }
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES Y FUNCIONES ---
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

def codificar_img(imagen):
    return base64.b64encode(imagen.read()).decode('utf-8')

# --- 3. DICCIONARIOS ---
ESPECIALIDADES = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO Advisor.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA.", "Seguridad": "Seguridad."}
TONOS = {"Analítica": "Lógica.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}

if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_data" not in st.session_state: st.session_state.pdf_data = ""

# --- 4. BARRA LATERAL (CENTRO DE CONTROL) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            try: supabase.table("chats").insert({"user_email": "Invitado", "messages": st.session_state.messages}).execute()
            except: pass
        st.session_state.messages = []; st.session_state.pdf_data = ""; st.rerun()
    
    st.divider()
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #ff4b4b; font-size: 0.7rem; font-weight: bold;'>CARGA DE MEDIOS</p>", unsafe_allow_html=True)
    pdf_up = st.file_uploader("SUBIR PDF:", type=['pdf'], accept_multiple_files=True)
    img_up = st.file_uploader("SUBIR FOTO:", type=['png', 'jpg', 'jpeg'])
    
    if pdf_up:
        st.session_state.pdf_data = extraer_pdf(pdf_up)
        st.caption("✅ PDF asimilado.")

    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}..."): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
def enviar_comando(label):
    sys_inst = f"Identidad: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}."
    st.session_state.messages.append({"role": "user", "content": f"Ejecuta: {label}"})
    c = client.chat.completions.create(messages=[{"role":"system","content": sys_inst}] + st.session_state.messages[-5:], model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content}); st.rerun()

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_comando(labels[i])

st.divider()

for msg in st.session_state.messages:
    if "Identidad:" not in msg["content"] and "Ejecuta:" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

# --- 6. LÓGICA DE RESPUESTA ---
if prompt := st.chat_input(f"Hablando con RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        # Inyección de personalidad y PDF
        contexto = f"\nDOC CARGADO: {st.session_state.pdf_data[:3500]}" if st.session_state.pdf_data else ""
        sys_i = f"Eres RUTH. Rol: {ESPECIALIDADES[esp_act]} Tono: {TONOS[ton_act]}. {contexto}"
        
        if img_up:
            b64 = codificar_img(img_up)
            c = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role":"system","content":sys_i}, {"role":"user","content":[{"type":"text","text":prompt}, {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]
            )
        else:
            c = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:]
            )
        
        res = c.choices[0].message.content
        st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
