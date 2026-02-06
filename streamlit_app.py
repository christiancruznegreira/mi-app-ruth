import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os

# --- 1. BRANDING (SE CARGA SÍ O SÍ) ---
st.set_page_config(page_title="RUTH Professional", page_icon="●")

# Título y Subtítulo directos
st.markdown("<h1 style='text-align: center; color: #ff4b4b; letter-spacing: 0.5rem;'>R U T H</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; letter-spacing: 0.1rem; font-weight: bold;'>INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</p>", unsafe_allow_html=True)
st.divider()

# --- 2. BARRA LATERAL (BOTÓN DE REINICIO) ---
with st.sidebar:
    st.header("SISTEMA")
    if st.button("REINICIAR TODO"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    st.write("Fecha: 6 de Febrero, 2026")

# --- 3. LÓGICA DE BÚSQUEDA ---
def obtener_datos_web(query):
    try:
        with DDGS() as ddgs:
            # Simplificamos la búsqueda al máximo
            results = ddgs.text(f"{query} noticias 2026", max_results=3)
            return "\n".join([r['body'] for r in results])
    except:
        return "No hay datos recientes disponibles."

# --- 4. CONFIGURACIÓN DE IA ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. INTERACCIÓN ---
if prompt := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ¿Es una pregunta de actualidad?
        info_web = ""
        if any(x in prompt.lower() for x in ["pasó", "noticia", "enero", "febrero", "2026", "hoy", "actual"]):
            with st.spinner("Buscando en la red..."):
                info_web = obtener_datos_web(prompt)

        # FORZAMOS A LA IA A SER ACTUAL
        instruccion_maestra = (
            "Eres RUTH, una IA actualizada al 6 de febrero de 2026. "
            f"Aquí tienes datos reales de internet: {info_web}. "
            "PROHIBIDO decir que tu conocimiento es hasta 2023. Responde usando los datos de internet."
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": instruccion_maestra},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            respuesta = chat_completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error técnico: {e}")
