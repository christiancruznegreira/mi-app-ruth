import streamlit as st
from groq import Groq
from supabase import create_client, Client
from fpdf import FPDF
import os
import datetime

# --- 1. ESTÉTICA PREMIUM (NEÓN ROJO Y PATRÓN) ---
st.set_page_config(page_title="RUTH Pro", page_icon="●", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }

    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow: 0 0 4px #f00, 0 0 11px #f00, 0 0 19px #f00, 0 0 40px #f00;
            color: #ff4b4b;
        }
        20%, 24%, 55% { text-shadow: none; color: #330000; }
    }
    .ruth-header { text-align: center; padding-top: 1rem; color: #ff4b4b; font-size: 5rem; animation: flicker 3s infinite alternate; font-weight: 100; letter-spacing: 1.2rem; }
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 3rem; font-weight: bold;}

    /* BOTONES GHOST MINIMALISTAS */
    .stButton>button {
        border: none !important; background-color: transparent !important; color: #aaaaaa !important; 
        width: 100% !important; height: 40px !important; transition: 0.2s ease;
        text-transform: uppercase; font-size: 0.48rem !important; font-weight: 400 !important;
        white-space: nowrap !important; cursor: pointer;
    }
    @keyframes text-flicker {
        0%, 100% { color: #ff4b4b; text-shadow: 0 0 8px #ff0000; }
        50% { color: #660000; text-shadow: none; }
    }
    .stButton>button:hover { animation: text-flicker 0.4s infinite; }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    
    /* Flecha de rescate */
    [data-testid="stSidebarCollapsedControl"] { background-color: #ff4b4b !important; color: white !important; border-radius: 0 10px 10px 0; left: 0; top: 15px; padding: 5px; display: flex; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIOS DE CONOCIMIENTO ---
ESPECIALIDADES = {
    "Abogada": "como Abogada Senior de Élite experta en leyes y jurisprudencia.",
    "Amazon Pro": "como Especialista en Amazon FBA, algoritmo A9 y e-commerce.",
    "Marketing": "como Directora de Marketing y experta en Copywriting persuasivo.",
    "Estratega": "como CEO Advisor y estratega de negocios internacionales.",
    "Médico": "como Médico Especialista con profundo conocimiento en ciencias de la salud.",
    "Finanzas": "como Analista de Inversiones y Wealth Manager.",
    "IA Pro": "como Arquitecto de IA y experto en ingeniería de prompts.",
    "Seguridad": "como Experto en Ciberseguridad y Privacidad de datos."
}

TONOS = {
    "Analítica": "Tono lógico, frío y basado estrictamente en datos.",
    "Sarcástica": "Tono cínico, mordaz e inteligente.",
    "Empática": "Tono suave, cálido y paciente.",
    "Motivadora": "Tono enérgico, inspirador y positivo.",
    "Ejecutiva": "Tono sobrio, breve y directo al grano.",
    "Conspiranoica": "Tono suspicaz y detectivesco."
}

# --- 3. CONEXIONES ---
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
    st.markdown("<h2 style='color: white; font-weight: 200; font-size: 1.2rem;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    especialidad = st.selectbox("ESPECIALIDAD:", list(ESPECIALIDADES.keys()))
    personalidad = st.selectbox("PERSONALIDAD:", list(TONOS.keys()))
    
    # BIBLIOTECA DINÁMICA CORREGIDA
    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>BIBLIOTECA</p>", unsafe_allow_html=True)
    if st.button("RECOMENDAR LITERATURA"):
        # Creamos una instrucción que fuerce el cambio de especialidad
        instruccion_biblioteca = (
            f"DIRECTIVA PRIORITARIA: Ignora cualquier rol anterior. "
            f"Actúa AHORA MISMO {ESPECIALIDADES[especialidad]} con un {TONOS[personalidad]}. "
            f"Recomiéndame 3 libros fundamentales de TU área actual ({especialidad}). "
            f"Indica cuál es de acceso gratuito y cuáles son de pago."
        )
        # Añadimos al historial para que el usuario vea la petición
        st.session_state.messages.append({"role": "user", "content": f"Solicitud de libros de {especialidad}"})
        
        # Llamada a la IA con la nueva especialidad forzada
        c = client.chat.completions.create(
            messages=[{"role":"system","content": instruccion_biblioteca}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
        st.rerun()

    st.divider()
    st.markdown("<p style='color: #888; font-size: 0.7rem;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    try:
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        for chat in res.data:
            m_u = chat['messages'][0]['content'][:20].upper()+"..." if chat['messages'] else "VACÍO"
            if st.button(f"{m_u}", key=chat['id']):
                st.session_state.messages = chat['messages']; st.rerun()
    except: pass

# --- 5. CUERPO PRINCIPAL ---
def enviar_c(t):
    # Inyección de personalidad forzada en botones
    sys_inst = f"Identidad TOTAL: {ESPECIALIDADES[especialidad]} Tono ABSOLUTO: {TONOS[personalidad]}. Responde ahora."
    st.session_state.messages.append({"role": "user", "content": t})
    c = client.chat.completions.create(messages=[{"role":"system","content": sys_inst}] + st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})

cols = st.columns(8); labels = list(ESPECIALIDADES.keys())
for i in range(8):
    with cols[i]:
        if st.button(labels[i].upper()): enviar_c(f"Ejecuta análisis como {labels[i]}"); st.rerun()

st.divider()

# --- 6. CHAT LOOP ---
for msg in st.session_state.messages:
    if "Identidad TOTAL" not in msg["content"] and "DIRECTIVA PRIORITARIA" not in msg["content"]:
        av = ruth_avatar if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])

if prompt := st.chat_input(f"RUTH {especialidad}"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant", avatar=ruth_avatar):
        # Inyección de personalidad forzada en chat manual
        sys_inst = f"Eres RUTH. Rol: {ESPECIALIDADES[especialidad]} Tono: {TONOS[personalidad]}. Olvida roles anteriores."
        c = client.chat.completions.create(messages=[{"role":"system","content": sys_inst}] + st.session_state.messages, model="llama-3.3-70b-versatile")
        res = c.choices[0].message.content
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
