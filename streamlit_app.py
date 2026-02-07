import streamlit as st
from groq import Groq
from supabase import create_client, Client
from PyPDF2 import PdfReader
import base64
import os
import datetime

# --- 1. CONFIGURACIÓN Y ESTÉTICA (SISTEMA DE RESCATE) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fondo Premium */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    /* FLECHA DE RESCATE ROJA (MÁXIMA PRIORIDAD) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #ff4b4b !important; color: white !important;
        border-radius: 0 10px 10px 0 !important; left: 0 !important;
        top: 20px !important; width: 50px !important; height: 45px !important;
        display: flex !important; justify-content: center !important; 
        align-items: center !important; z-index: 999999 !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
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

def extraer_pdf(archivos):
    texto = ""
    for a in archivos:
        try:
            r = PdfReader(a)
            for p in r.pages: texto += p.extract_text() + "\n"
        except: pass
    return texto

if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_data" not in st.session_state: st.session_state.pdf_data = ""

# --- 3. BARRA LATERAL (CONTROL CENTER) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            try: supabase.table("chats").insert({"user_email": "Invitado", "messages": st.session_state.messages}).execute()
            except: pass
        st.session_state.messages = []; st.session_state.pdf_data = ""; st.rerun()
    
    st.divider()
    ESPECIALIDADES = {"Abogada": "Abogada.", "Amazon Pro": "Amazon.", "Marketing": "Marketing.", "Estratega": "CEO Advisor.", "Médico": "Médico.", "Finanzas": "Finanzas.", "IA Pro": "IA.", "Seguridad": "Seguridad."}
    TONOS = {"Analítica": "Lógica.", "Sarcástica": "Cínica.", "Empática": "Suave.", "Motivadora": "Éxito.", "Ejecutiva": "ROI.", "Conspiranoica": "Oculto."}
    
    esp_act = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    ton_act = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #ff4b4b; font-size: 0.7rem; font-weight: bold;'>CARGA DE MEDIOS</p>", unsafe_allow_html=True)
    pdf_up = st.file_uploader("PDF TÉCNICO:", type=['pdf'], accept_multiple_files=True)
    img_up = st.file_uploader("ANALIZAR FOTO:", type=['png', 'jpg', 'jpeg'])
    
    if pdf_up:
        st.session_state.pdf_data = extraer_pdf(pdf_up)
        st.caption("✅ PDF analizado.")

    st.divider()
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            tit = chat['messages'][0]['content'][:15].upper() if chat['messages'] else "VACÍO"
            if st.button(f"{tit}..."): st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 4. LÓGICA DE BOTONES SUPERIORES ---
def enviar_c(label):
    st.session_state.messages.append({"role": "user", "content": f"Ejecuta análisis como {label}"})
    sys_i = f"Eres RUTH {ESPECIALIDADES[esp_act]} ({TONOS[ton_act]})."
    c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:])
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content}); st.rerun()

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_c(labels[i])

st.divider()

# --- 5. CHAT LOOP ---
for msg in st.session_state.messages:
    if "Ejecuta análisis" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

# --- 6. PROCESAMIENTO CON FALLBACK (VISIÓN BLINDADA) ---
if prompt := st.chat_input(f"RUTH {esp_act}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=ruth_avatar):
        contexto = f"\nDOC: {st.session_state.pdf_data[:3000]}" if st.session_state.pdf_data else ""
        sys_i = f"Eres RUTH {ESPECIALIDADES[esp_act]} {TONOS[ton_act]}. {contexto}"
        
        try:
            if img_up:
                b64_img = base64.b64encode(img_up.getvalue()).decode('utf-8')
                # INTENTO 1: Modelo de producción estable
                try:
                    modelo_vision = "llama-3.2-11b-vision-instruct" 
                    c = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [{"type": "text", "text": f"{sys_i}\n\n{prompt}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                    )
                except:
                    # FALLBACK: Modelo alternativo si el primero falla
                    modelo_vision = "llava-v1.5-7b-4096-preview"
                    c = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{"role": "user", "content": [{"type": "text", "text": f"{sys_i}\n\n{prompt}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
                    )
            else:
                c = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_i}] + st.session_state.messages[-5:])
            
            res = c.choices[0].message.content
            st.markdown(res); st.session_state.messages.append({"role": "assistant", "content": res})
        except Exception as e:
            st.error(f"Error de conexión con la IA. Inténtalo de nuevo en unos segundos.")
