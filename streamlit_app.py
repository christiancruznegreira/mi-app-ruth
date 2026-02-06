import streamlit as st
from groq import Groq
import os
import datetime
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN Y ESTÉTICA PREMIUM
st.set_page_config(page_title="RUTH Ultra", page_icon="●", layout="wide")

st.markdown("""
    <style>
    /* Fondo con Patrón */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* Ocultar elementos de Streamlit */
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden !important; }

    /* Branding RUTH */
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}

    /* Botones de Acción Rápida */
    .stButton>button {
        border-radius: 20px !important;
        border: 1px solid #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.05) !important;
        color: white !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">ULTRA PROFESSIONAL SUITE</div>
""", unsafe_allow_html=True)

# 2. GESTIÓN DE MEMORIA
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = {}

# Función para procesar la orden del usuario
def procesar_prompt(texto_usuario):
    st.session_state.messages.append({"role": "user", "content": texto_usuario})
    
    # Llamada a la IA
    client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    sys_msg = "Eres RUTH, una IA profesional de élite. Responde con elegancia y precisión."
    full_msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
    
    try:
        completion = client.chat.completions.create(
            messages=full_msgs,
            model="llama-3.3-70b-versatile"
        )
        respuesta = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
    except Exception as e:
        st.error(f"Error: {e}")

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            id_c = datetime.datetime.now().strftime("%H:%M")
            st.session_state.history[f"Chat {id_c}"] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    uploaded_file = st.file_uploader("📄 Analizador de PDF", type="pdf")

# 4. BOTONES DE ACCIÓN RÁPIDA (INTERFAZ)
col1, col2, col3, col4 = st.columns(4)

# Aquí está la corrección: cada botón llama a la función procesar_prompt
with col1:
    if st.button("📝 Redactar Email"):
        procesar_prompt("RUTH, redacta un email profesional elegante para un cliente importante.")
        st.rerun()
with col2:
    if st.button("⚖️ Revisar Cláusula"):
        procesar_prompt("RUTH, analicemos esta cláusula legal. ¿Es segura y estándar?")
        st.rerun()
with col3:
    if st.button("📦 SEO Amazon"):
        procesar_prompt("RUTH, optimiza el SEO de este producto para Amazon: incluye título, bullet points y keywords.")
        st.rerun()
with col4:
    if st.button("💡 Nueva Estrategia"):
        procesar_prompt("RUTH, propón una estrategia de negocio disruptiva para aumentar las ventas este mes.")
        st.rerun()

st.divider()

# 5. MOSTRAR CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de texto manual
if prompt := st.chat_input("Consulta a RUTH Ultra..."):
    procesar_prompt(prompt)
    st.rerun()
