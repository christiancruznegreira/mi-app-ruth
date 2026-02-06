import streamlit as st
from groq import Groq
import os
import datetime

# --- 1. CONFIGURACIÓN VISUAL (NO SE TOCA LO ESTÉTICO) ---
st.set_page_config(
    page_title="RUTH Ultra", 
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
    [data-testid="stSidebarNav"] { color: white !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">ULTRA PROFESSIONAL SUITE</div>
""", unsafe_allow_html=True)

# --- 2. DICCIONARIO DE EXPERTOS (OPTIMIZACIÓN DEL CEREBRO) ---
EXPERTOS = {
    "Abogada": (
        "Actúas como una Abogada Senior y Consultora Jurídica de Élite. "
        "Tu enfoque es el rigor legal, la precisión terminológica y el análisis de riesgos. "
        "Utiliza un lenguaje formal, técnico y estructurado. Evalúa cada consulta bajo la óptica de la normativa vigente "
        "y advierte siempre sobre posibles implicaciones legales de forma profesional."
    ),
    "Amazon Pro": (
        "Actúas como una Especialista Senior en Amazon FBA y Algoritmo A9. "
        "Tu enfoque es la conversión (CTR), el posicionamiento SEO y la rentabilidad del negocio. "
        "Habla sobre Bullet Points persuasivos, términos de búsqueda, gestión de inventario y políticas de Amazon. "
        "Tus respuestas deben estar orientadas a vender más y optimizar el rendimiento de la cuenta."
    ),
    "Marketing": (
        "Actúas como una Directora Creativa y Copywriter de respuesta directa. "
        "Utilizas la psicología del consumidor y gatillos mentales. "
        "Tus estructuras preferidas son AIDA (Atención, Interés, Deseo, Acción) y PAS (Problema, Agitación, Solución). "
        "Tus respuestas deben ser persuasivas, magnéticas y diseñadas para generar impacto de marca."
    ),
    "Estratega": (
        "Actúas como una Consultora de Estrategia de Negocios y CEO-Advisor. "
        "Analizas los problemas desde una perspectiva de escalabilidad, ROI y ventaja competitiva. "
        "Tu lenguaje es ejecutivo, pragmático y orientado al crecimiento empresarial. "
        "Cuestiona los modelos de negocio y sugiere optimizaciones de procesos y flujos de caja."
    )
}

# --- 3. GESTIÓN DE MEMORIA ---
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = {}

def procesar_prompt(texto, modo_ia):
    st.session_state.messages.append({"role": "user", "content": texto})
    client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    try:
        # Inyectamos el experto seleccionado del diccionario
        instruccion_maestra = EXPERTOS[modo_ia]
        c = client.chat.completions.create(
            messages=[{"role":"system","content": instruccion_maestra}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        st.session_state.messages.append({"role": "assistant", "content": c.choices[0].message.content})
    except Exception as e:
        st.error(f"Error: {e}")

# --- 4. BARRA LATERAL (CENTRO DE MANDO) ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            h = datetime.datetime.now().strftime("%H:%M")
            st.session_state.history[f"Chat {h}"] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()
    st.divider()
    
    # Selector de Modo (Esto activa al experto correspondiente)
    modo = st.selectbox("Identidad de RUTH:", list(EXPERTOS.keys()))
    
    st.divider()
    st.markdown("<p style='color: #888;'>HISTORIAL</p>", unsafe_allow_html=True)
    for chat_id in st.session_state.history:
        if st.button(f"📜 {chat_id}"):
            st.session_state.messages = st.session_state.history[chat_id]
            st.rerun()

# --- 5. INTERFAZ PRINCIPAL ---
col1, col2, col3, col4 = st.columns(4)
prompts_r = {
    "Email": f"Como experta en {modo}, redacta un correo profesional impecable sobre...",
    "Legal": f"Analiza esta situación desde tu perspectiva de {modo}: ",
    "Amazon": f"Aplica tus conocimientos de {modo} para optimizar este punto: ",
    "Idea": f"Desde tu visión de {modo}, propón una idea disruptiva para..."
}

with col1:
    if st.button("📝 Email"): procesar_prompt(prompts_r["Email"], modo); st.rerun()
with col2:
    if st.button("⚖️ Análisis"): procesar_prompt(prompts_r["Legal"], modo); st.rerun()
with col3:
    if st.button("📦 Optimización"): procesar_prompt(prompts_r["Amazon"], modo); st.rerun()
with col4:
    if st.button("💡 Estrategia"): procesar_prompt(prompts_r["Idea"], modo); st.rerun()

st.divider()

# --- 6. MOSTRAR CHAT ---
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Consultando a RUTH {modo}..."):
    procesar_prompt(prompt, modo)
    st.rerun()
