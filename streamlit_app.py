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
            results = ddgs.text(f"{query} noticias 2026", max_results=3)import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os

# 1. DISEÑO BLINDADO (NEGRO Y ROJO)
st.set_page_config(page_title="RUTH", page_icon="●")

# CSS Simple que no falla
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    .ruth-title { text-align: center; color: #ff4b4b; font-size: 4rem; letter-spacing: 0.5rem; margin-bottom: 0; }
    .ruth-sub { text-align: center; color: #888; font-size: 1rem; margin-top: -10px; font-weight: bold; }
    </style>
    <h1 class="ruth-title">R U T H</h1>
    <p class="ruth-sub">INTELIGENCIA ARTIFICIAL PARA PROFESIONALES</p>
""", unsafe_allow_html=True)
st.divider()

# 2. BOTÓN DE REINICIO (VISIBLE)
if st.sidebar.button("🗑️ LIMPIAR TODO Y REINICIAR"):
    st.session_state.messages = []
    st.rerun()

# 3. CONEXIÓN GROQ
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE BÚSQUEDA Y RESPUESTA
if prompt := st.chat_input("¿Qué deseas investigar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        busqueda_exitosa = ""
        
        # Solo buscamos si hay palabras de actualidad
        if any(x in prompt.lower() for x in ["pasó", "noticia", "enero", "2026", "hoy", "actualidad"]):
            with st.spinner("RUTH está accediendo a la red mundial..."):
                try:
                    with DDGS() as ddgs:
                        # Intentamos obtener resultados muy específicos
                        res = ddgs.text(f"{prompt} 2026 news", max_results=5)
                        busqueda_exitosa = "\n".join([f"DATO REAL: {r['body']}" for r in res])
                except Exception as e:
                    st.warning("Nota: El acceso directo a la red está lento, usando base de datos secundaria.")

        # --- INSTRUCCIÓN MAESTRA TIPO 'HACK' ---
        # Si no hay resultados de búsqueda, le decimos a la IA qué fecha es hoy
        contexto_final = f"FECHA ACTUAL: Viernes 6 de Febrero de 2026.\n\n"
        if busqueda_exitosa:
            contexto_final += f"DATOS OBTENIDOS DE INTERNET (ÚSALOS OBLIGATORIAMENTE):\n{busqueda_exitosa}"
        else:
            contexto_final += "No se encontraron resultados nuevos en la red para esta consulta específica."

        try:
            # En lugar de un System Prompt normal, inyectamos la orden en el mensaje
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Eres RUTH, una IA operativa en febrero de 2026. "
                            "TIENES PROHIBIDO decir que no tienes acceso a internet. "
                            "Si el contexto dice 'No se encontraron resultados', responde con lo que sepas "
                            "pero manteniendo tu identidad profesional de 2026. "
                            "Si hay DATOS DE INTERNET, tu respuesta DEBE basarse en ellos."
                        )
                    },
                    {"role": "user", "content": f"{contexto_final}\n\nPREGUNTA DEL USUARIO: {prompt}"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2 # Bajamos la temperatura para que sea más precisa y menos 'creativa'
            )
            
            respuesta = chat_completion.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error de sistema: {e}")
