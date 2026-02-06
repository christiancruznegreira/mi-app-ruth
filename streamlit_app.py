import streamlit as st
from groq import Groq
import os

# 1. ESTÉTICA PREMIUM RUTH
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

# 2. PANEL LATERAL
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

# 3. DEFINICIÓN DE PERSONALIDADES ÉLITE
personalidades = {
    "Amazon FBA Pro (Ventas)": "Eres RUTH Amazon Experta. Tu tono es analítico y audaz. Te enfocas en SEO y ventas.",
    "Legal & Contratos (Asistente)": "Eres RUTH Legal. Tu tono es preciso, formal y técnico. Te enfocas en la exactitud jurídica.",
    "Copywriting & Ads (Marketing)": "Eres RUTH Copywriter. Tu tono es persuasivo y creativo. Te enfocas en la psicología de ventas.",
    "Educación & Tutoría (Académico)": "Eres RUTH Tutora. Tu tono es sabio, paciente y alentador. Te enfocas en simplificar lo complejo.",
    "Estrategia de Negocios (Socia)": "Eres RUTH Estratega. Tu tono es visionario y ejecutivo. Te enfocas en la escalabilidad y rentabilidad."
}

# 4. CEREBRO DE RUTH
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    av = ruth_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=av):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Modo: {negocio}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # Aquí inyectamos la personalidad según el modo elegido
            sys_prompt = f"{personalidades[negocio]} Responde con elegancia y mantén tu identidad como RUTH."
            mensajes_ia = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            
            completion = client.chat.completions.create(
                messages=mensajes_ia,
                model="llama-3.3-70b-versatile"
            )
            respuesta = completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error: {e}")
