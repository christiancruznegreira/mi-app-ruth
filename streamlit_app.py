import streamlit as st
from groq import Groq
import os
import urllib.parse
import random

# 1. ESTÉTICA PREMIUM (NEGRA CON PUNTOS Y TÍTULO ROJO)
st.set_page_config(page_title="RUTH", page_icon="●")
st.markdown("""
    <style>
    /* Fondo Oscuro con Puntos */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        background-image: radial-gradient(#1a1d24 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu, footer, header, .viewerBadge_container__1QS1n {visibility: hidden; display: none;}
    
    /* Título RUTH en ROJO ELEGANTE */
    .ruth-header {
        text-align: center; 
        padding-top: 2rem; 
        letter-spacing: 0.8rem; 
        font-weight: 200; 
        color: #ff4b4b; /* Rojo Streamlit / Premium */
        font-size: 3.5rem;
        text-shadow: 0px 0px 20px rgba(255, 75, 75, 0.2);
    }
    
    /* Color de texto */
    div[data-testid="stMarkdownContainer"] p {color: #e0e0e0 !important;}
    
    /* Ajuste de la caja de chat */
    .stChatInput {
        border: 1px solid #ff4b4b44 !important;
    }
    </style>
    <div class="ruth-header">R U T H</div>
""", unsafe_allow_html=True)

# 2. CONTROL LATERAL
with st.sidebar:
    if st.button("Reiniciar Sistema"):
        st.session_state.messages = []
        st.rerun()

# 3. CONEXIÓN
client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
icon_path = "logo_ruth.png"
ruth_avatar = icon_path if os.path.exists(icon_path) else "●"

# 4. MEMORIA CONVERSACIONAL (SIN FORZAR IMÁGENES)
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres RUTH, una asistente sofisticada y conversacional. Habla de forma elegante y humana. "
                       "SOLO si el usuario pide explícitamente una imagen, foto o dibujo, añade al final de tu respuesta: 'DIBUJO: [descripción en inglés]'. "
                       "Si no te piden una imagen, limítate a hablar normalmente."
        }
    ]

def get_image_url(prompt_text):
    clean_prompt = prompt_text.replace("DIBUJO:", "").strip()
    prompt_enc = urllib.parse.quote(clean_prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{prompt_enc}?width=1024&height=1024&seed={seed}&nologo=true"

# 5. MOSTRAR CHAT
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar=(ruth_avatar if msg["role"]=="assistant" else None)):
            # Solo intentamos mostrar imagen si el comando existe en el mensaje
            if "DIBUJO:" in msg["content"]:
                partes = msg["content"].split("DIBUJO:")
                texto = partes[0].strip()
                comando = partes[1].strip()
                if texto: st.markdown(texto)
                st.image(get_image_url(comando), use_container_width=True)
            else:
                st.markdown(msg["content"])

# 6. INTERACCIÓN
if prompt := st.chat_input("Escribe tu consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=ruth_avatar):
        try:
            # La IA responde
            response = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
            
            # Verificamos si el usuario pidió imagen para evitar errores
            palabras_clave = ["imagen", "dibujo", "foto", "dibuja", "muéstrame", "crea"]
            pide_imagen = any(palabra in prompt.lower() for palabra in palabras_clave)

            # Si hay comando de dibujo en la respuesta, lo mostramos
            if "DIBUJO:" in response and pide_imagen:
                partes = response.split("DIBUJO:")
                texto = partes[0].strip()
                comando = partes[1].strip()
                if texto: st.markdown(texto)
                st.image(get_image_url(comando), use_container_width=True)
            else:
                # Si la IA puso DIBUJO: por error sin que se lo pidieran, lo limpiamos
                clean_response = response.split("DIBUJO:")[0].strip()
                st.markdown(clean_response)
                response = clean_response
                
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")
