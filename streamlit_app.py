import streamlit as st
from groq import Groq
import os

# --- 1. ESTÉTICA PREMIUM RUTH (ROJO Y NEGRO) ---
st.set_page_config(page_title="RUTH Business Suite", page_icon="●", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}
    .ruth-header {
        text-align: center; padding-top: 1rem; letter-spacing: 0.8rem; 
        font-weight: 200; color: #ff4b4b; font-size: 3.5rem; margin-bottom: 0px;
    }
    .ruth-subtitle {
        text-align: center; color: #888; font-size: 0.8rem; 
        margin-top: -10px; letter-spacing: 0.3rem; margin-bottom: 2rem;
    }
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; font-size: 1.05rem; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# --- 2. SELECTOR DE UNIDAD DE NEGOCIO ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff4b4b;'>CENTRO DE MANDO</h2>", unsafe_allow_html=True)
    negocio = st.selectbox(
        "Activar Módulo:",
        [
            "Amazon FBA Pro (Ventas)",
            "Legal & Contratos (Asistente)",
            "Copywriting & Ads (Marketing)",
            "Educación & Tutoría (Académico)",
            "Estrategia de Negocios (Socia)"
        ]
    )
    
    st.divider()
    if st.button("🔄 REINICIAR CONSOLA"):
        st.session_state.messages = []
        st.rerun()
    
    st.info("💡 Estrategia Pro: Pega noticias de 2026 y RUTH las analizará con su lógica avanzada.")

# --- 3. CONFIGURACIÓN DEL CEREBRO ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# Definición de las personalidades de RUTH
personalidades = {
    "Amazon FBA Pro (Ventas)": "Eres RUTH Amazon Experta. Tu especialidad es el SEO de Amazon, redacción de listados que convierten y análisis de competencia. Ayudas a vendedores a ganar dinero.",
    "Legal & Contratos (Asistente)": "Eres RUTH Legal. Tu especialidad es redactar borradores de contratos, analizar cláusulas y resumir documentos legales complejos con precisión técnica.",
    "Copywriting & Ads (Marketing)": "Eres RUTH Copywriter. Usas fórmulas de psicología de ventas (AIDA, PAS) para escribir anuncios, hilos de Twitter y correos que venden.",
    "Educación & Tutoría (Académico)": "Eres RUTH Tutora. Explicas temas complejos de forma sencilla, creas exámenes de práctica y planes de estudio personalizados.",
    "Estrategia de Negocios (Socia)": "Eres RUTH Business Strategist. Analizas modelos de negocio, realizas análisis DAFO y sugieres estrategias de crecimiento para startups."
}

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar Chat
for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

# --- 4. INTERACCIÓN ---
if prompt := st.chat_input(f"Trabajando en modo: {negocio}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # Instrucción Maestra según el negocio seleccionado
            system_prompt = (
                f"{personalidades[negocio]} "
                "Tu conocimiento base llega a 2023, pero eres capaz de procesar cualquier información de 2026 que el usuario te proporcione en el chat. "
                "Responde siempre con un tono profesional, elegante y minimalista."
            )
            
            mensajes_ia = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            completion = client.chat.completions.create(
                messages=mensajes_ia,
                model="llama-3.3-70b-versatile",
            )
            
            respuesta = completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error de sistema: {e}")
