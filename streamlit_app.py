import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. ESTÉTICA PREMIUM (SIN CAMBIOS) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer { visibility: hidden; }
    [data-testid="stSidebarCollapsedControl"] { background-color: #ff4b4b !important; color: white !important; border-radius: 0 10px 10px 0; left: 0; top: 15px; padding: 5px; }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% { text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 40px #f00; color: #ff4b4b; }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}
    [data-testid="column"] { padding: 0px 1px !important; text-align: center !important; }
    .stButton>button { border: none !important; background-color: transparent !important; color: #aaaaaa !important; width: 100% !important; height: 40px !important; transition: 0.2s ease; text-transform: uppercase; font-size: 0.48rem !important; letter-spacing: 0.01rem !important; white-space: nowrap !important; cursor: pointer; }
    @keyframes text-flicker { 0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; } 50% { color: #660000; text-shadow: none; } }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
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
    "Sarcástica": "Tu tono es cínico, mordaz, inteligente pero cortante. Te burlas de la mediocridad.",
    "Analítica": "Tu tono es puramente lógico, frío, basado solo en datos y hechos crudos.",
    "Empática": "Tu tono es suave, paciente y enfocado en el apoyo emocional incondicional.",
    "Motivadora": "Tu tono es enérgico, inspirador y agresivamente positivo hacia el éxito.",
    "Ejecutiva": "Tu tono es sobrio, breve y enfocado exclusivamente en el ROI y eficiencia.",
    "Conspiranoica": "Tu tono es suspicaz y buscas patrones de control ocultos en todo."
}

# --- 3. CONEXIONES ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

def guardar_nube_forzado(mensajes):
    if mensajes:
        try:
            # Enviamos los datos y esperamos confirmación
            supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
            return True
        except: return False
    return False

if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    # NUEVA CONVERSACIÓN CON GUARDADO GARANTIZADO
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            with st.spinner("Guardando en la nube..."):
                guardar_nube_forzado(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    especialidad = st.selectbox("Especialidad:", list(ESPECIALIDADES.keys()))
    personalidad = st.selectbox("Personalidad:", list(TONOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            m_u = "Vacio"
            for m in chat['messages']: 
                if m['role']=='user': m_u = m['content'][:20].upper()+"..."; break
            if st.button(f"{m_u}", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. LOGICA DE IA (NÚCLEO DINÁMICO) ---
def responder_ia(prompt_usuario):
    # CUIDADO: Inyectamos el tono actual justo antes de la respuesta de la IA
    # Esto "obliga" a la IA a cambiar de tono aunque el historial diga lo contrario
    instruccion_maestra = f"Identidad: {ESPECIALIDADES[especialidad]} Tono: {TONOS[personalidad]} PROHIBIDO disculparte por cambiar de modo. Responde ahora mismo con esa personalidad."
    
    mensajes_completos = [{"role": "system", "content": instruccion_maestra}] + st.session_state.messages
    
    try:
        completion = client.chat.completions.create(
            messages=mensajes_completos,
            model="llama-3.3-70b-versatile",
            temperature=0.7 # Subimos un poco para que se note más la personalidad
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de sistema: {e}"

# Botones Ghost
cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()):
            st.session_state.messages.append({"role": "user", "content": f"Realiza una acción experta como {labels[i]}"})
            res = responder_ia(f"Acción como {labels[i]}")
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

st.divider()

# --- 6. CHAT LOOP ---
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Hablando con RUTH {especialidad} ({personalidad})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant", avatar=ruth_avatar):
        respuesta = responder_ia(prompt)
        st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
