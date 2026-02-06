import streamlit as st
from groq import Groq
import os
import datetime
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN Y ESTÉTICA GLASSMORPHISM
st.set_page_config(page_title="RUTH Ultra", page_icon="●", layout="wide")

st.markdown("""
    <style>
    /* Fondo Premium con Patrón */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }

    /* Efecto Glassmorphism en Mensajes */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 15px !important;
    }

    /* Barra de Herramientas Rápidas */
    .quick-tools {
        display: flex; gap: 10px; margin-bottom: 20px; justify-content: center;
    }
    
    /* Títulos y Branding */
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}

    /* Botones de Acción */
    .stButton>button {
        border-radius: 20px !important;
        border: 1px solid #ff4b4b !important;
        background-color: transparent !important;
        color: white !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ff4b4b !important; }
    </style>
""", unsafe_allow_html=True)

# 2. BARRA LATERAL (WORKSPACE)
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = {}

with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            id_c = datetime.datetime.now().strftime("%H:%M")
            st.session_state.history[f"Chat {id_c}"] = st.session_state.messages
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    modulo = st.selectbox("Especialidad:", ["Legal", "Amazon FBA", "Marketing", "Estrategia"])
    
    # CARGA DE ARCHIVOS
    st.markdown("### 📄 ANALIZADOR")
    uploaded_file = st.file_uploader("Sube un PDF para que RUTH lo analice", type="pdf")
    
    st.divider()
    if st.session_state.history:
        st.markdown("### HISTORIAL")
        for h in st.session_state.history:
            if st.button(f"📜 {h}"):
                st.session_state.messages = st.session_state.history[h]
                st.rerun()

# 3. INTERFAZ PRINCIPAL
st.markdown('<div class="ruth-header">R U T H</div>', unsafe_allow_html=True)
st.markdown('<div class="ruth-subtitle">ULTRA PROFESSIONAL SUITE</div>', unsafe_allow_html=True)

# BARRA DE HERRAMIENTAS RÁPIDAS
col1, col2, col3, col4 = st.columns(4)
with col1: 
    if st.button("📝 Redactar Email"): prompt_rapido = "RUTH, redacta un email profesional sobre..."
with col2:
    if st.button("⚖️ Revisar Cláusula"): prompt_rapido = "RUTH, analiza si esta cláusula es segura: "
with col3:
    if st.button("📦 SEO Amazon"): prompt_rapido = "RUTH, optimiza el SEO de este producto: "
with col4:
    if st.button("💡 Nueva Estrategia"): prompt_rapido = "RUTH, dame una estrategia disruptiva para..."

# 4. LÓGICA DE PROCESAMIENTO
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Si se sube un archivo, leerlo
contexto_archivo = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        contexto_archivo += page.extract_text()
    st.success("Archivo procesado. RUTH ahora tiene el contexto del documento.")

# Mostrar Chat
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# Entrada de Usuario
if prompt := st.chat_input("Consulta a RUTH Ultra..."):
    # Si hay un archivo cargado, lo inyectamos en la pregunta
    if contexto_archivo:
        prompt_final = f"CONTEXTO DEL ARCHIVO SUBIDO:\n{contexto_archivo}\n\nPREGUNTA SOBRE EL ARCHIVO: {prompt}"
    else:
        prompt_final = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            sys_msg = f"Eres RUTH, modo {modulo}. Eres experta en análisis profesional."
            full_msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            # Reemplazamos el último mensaje con el que tiene el contexto del archivo
            full_msgs[-1]["content"] = prompt_final
            
            completion = client.chat.completions.create(messages=full_msgs, model="llama-3.3-70b-versatile")
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
        except Exception as e:
            st.error(f"Error: {e}")
