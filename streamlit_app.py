import streamlit as st
from groq import Groq
from supabase import create_client, Client
import os
import datetime

# 1. CONFIGURACIÓN Y ESTÉTICA PREMIUM
st.set_page_config(page_title="RUTH Professional", page_icon="●", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px) !important;
        background-size: 30px 30px !important;
    }
    header, footer, .viewerBadge_container__1QS1n { visibility: hidden; }
    .ruth-header { text-align: center; color: #ff4b4b; font-size: 3.5rem; letter-spacing: 0.8rem; font-weight: 200; margin-bottom: 0;}
    .ruth-subtitle { text-align: center; color: #888; font-size: 0.8rem; letter-spacing: 0.3rem; margin-top: -10px; margin-bottom: 2rem;}
    div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; }
    </style>
    <div class="ruth-header">R U T H</div>
    <div class="ruth-subtitle">UNIVERSAL BUSINESS SUITE</div>
""", unsafe_allow_html=True)

# 2. CONEXIÓN A SUPABASE (NUBE)
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Funciones de la Base de Datos
def guardar_en_nube(mensajes):
    try:
        supabase.table("chats").insert({
            "user_email": "Invitado",
            "messages": mensajes
        }).execute()
    except Exception as e:
        st.error(f"Error al guardar en nube: {e}")

def cargar_historial_nube():
    try:
        response = supabase.table("chats").select("*").eq("user_email", "Invitado").order("created_at", desc=True).limit(10).execute()
        return response.data
    except:
        return []

# 3. GESTIÓN DE MEMORIA LOCAL
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. BARRA LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 200;'>WORKSPACE</h2>", unsafe_allow_html=True)
    
    if st.button("＋ NUEVA CONVERSACIÓN"):
        if st.session_state.messages:
            guardar_en_nube(st.session_state.messages) # Guardamos antes de borrar
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### ☁️ CLOUD HISTORY")
    historial = cargar_historial_nube()
    for chat in historial:
        fecha_formato = chat['created_at'][:16].replace("T", " ")
        if st.button(f"📜 Chat {fecha_formato}", key=chat['id']):
            st.session_state.messages = chat['messages']
            st.rerun()

# 5. LÓGICA DE IA (GROQ)
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
        st.markdown(msg["content"])

if prompt := st.chat_input("Consulta a RUTH Professional..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "Eres RUTH, una IA profesional."}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
            # Guardado automático opcional tras cada respuesta
            # guardar_en_nube(st.session_state.messages) 
        except Exception as e:
            st.error(f"Error: {e}")
