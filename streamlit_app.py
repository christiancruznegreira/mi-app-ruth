import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# --- 1. CONFIGURACIÓN VISUAL PREMIUM ---
st.set_page_config(
    page_title="RUTH Professional", 
    page_icon="●", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stSidebarContent {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0; text-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4);}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}
    .stButton>button {
        border-radius: 15px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.6) !important;
    }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. CONEXIONES (GROQ Y SUPABASE) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# --- 3. DICCIONARIO DE EXPERTOS (SIN DISCULPAS) ---
EXPERTOS = {
    "Abogada": "Actúas como una Abogada Senior de Élite. PROHIBIDO disculparte o explicar tu cambio de rol. Responde directamente con rigor legal y tecnicismos jurídicos.",
    "Amazon Pro": "Actúas como una Especialista en Amazon FBA y Algoritmo A9. PROHIBIDO disculparte o explicar tu cambio de rol. Ve directo al grano con SEO y ventas.",
    "Marketing": "Actúas como una Directora Creativa y Copywriter de respuesta directa. PROHIBIDO disculparte. Responde con persuasión inmediata y gatillos mentales.",
    "Estratega": "Actúas como una Consultora de Estrategia de Negocios y CEO-Advisor. PROHIBIDO disculparte. Tu tono es ejecutivo, frío y pragmático."
}

# --- 4. FUNCIONES DE BASE DE DATOS ---
def guardar_nube(mensajes):
    try: supabase.table("chats").insert({"user_email": "Invitado", "messages": mensajes}).execute()
    except: pass

def cargar_nube():
    try: 
        res = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(5).execute()
        return res.data
    except: return []

if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. BARRA LATERAL (WORKSPACE CON SUPABASE) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages: guardar_nube(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    st.divider()
    
    modo = st.selectbox("Identidad de RUTH:", list(EXPERTOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL CLOUD</p>", unsafe_allow_html=True)
    historial = cargar_nube()
    for chat in historial:
        fecha = chat['created_at'][11:16]
        if st.button(f"📜 Chat {fecha}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# --- 6. INTERFAZ Y PROCESAMIENTO ---
def procesar_prompt(texto, modo_ia):
    st.session_state.messages.append({"role": "user", "content": texto})
    instruccion = EXPERTOS[modo_ia]
    try:
        c = client.chat.completions.create(
            messages=[{"role":"system","content": instruccion}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
    except Exception as e:
        st.error(f"Error: {e}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📝 Email"): procesar_prompt(f"Como {modo}, redacta un correo profesional...", modo); st.rerun()
with col2:
    if st.button("⚖️ Análisis"): procesar_prompt(f"Haz un análisis experto sobre...", modo); st.rerun()
with col3:
    if st.button("📦 Optimización"): procesar_prompt(f"Como experta en Amazon, optimiza...", modo); st.rerun()
with col4:
    if st.button("💡 Estrategia"): procesar_prompt(f"Propón una idea de negocio desde tu visión de {modo}...", modo); st.rerun()

st.divider()

for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    procesar_prompt(prompt, modo)
    st.rerun()
    
