import streamlit as st
import json
import time
from pathlib import Path
from collections import deque
from select_relevant_pdf import seleccionar_pdf_relevante
from memory_manager import ConversationalMemory
from initial_document_selector import show_initial_selector
from hybrid_search import hybrid_search
from generate_answer_2 import generate_answer_streaming
from groq import Groq

# CONFIGURACIÓN
st.set_page_config(page_title="Vallegrancito", page_icon="assets/page_icon.jpg")

model_path = Path("huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf")
api_key = st.secrets["GROQ_API_KEY"]
assistant_avatar = "assets/default_user_photo.jpg"

# ESTADOS DE SESIÓN
if "memory" not in st.session_state:
    st.session_state.memory = ConversationalMemory()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_filename" not in st.session_state:
    st.session_state.selected_filename = None
if "partial_response" not in st.session_state:
    st.session_state.partial_response = ""
if "auto_intro_done" not in st.session_state:
    st.session_state.auto_intro_done = False
if "recent_interactions" not in st.session_state:
    st.session_state.recent_interactions = deque(maxlen=3)
if "selector_temp_choice" not in st.session_state:
    st.session_state.selector_temp_choice = None
if "last_summary" not in st.session_state:
    st.session_state.last_summary = ""
if "last_user_query" not in st.session_state:
    st.session_state.last_user_query = ""

# MOSTRAR MENÚ INICIAL SI NO SE HA ELEGIDO CARPETA
if st.session_state.selector_temp_choice is None:
    show_initial_selector()
    st.stop()

# SIDEBAR
from base64 import b64encode

def mostrar_logo_sidebar(image_path="assets/logo_completo.png"):
    with open(image_path, "rb") as img_file:
        encoded = b64encode(img_file.read()).decode()
    st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: -1.5rem;">
        <img src="data:image/png;base64,{encoded}" width="230" />
    </div>
    """, unsafe_allow_html=True)

mostrar_logo_sidebar()
#st.sidebar.caption("Sesión de chat")
st.sidebar.markdown("---")


#------Agregado
# Leer el catálogo de documentos
with open("document_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

# Crear mapeo de título ↔ filename
opciones = {item["title"]: item["filename"] for item in catalog}
inverted_opciones = {v: k for k, v in opciones.items()}

# Obtener el título actual según la selección guardada
titulo_actual = inverted_opciones.get(st.session_state.selector_temp_choice, list(opciones.keys())[0])

# Mostrar selectbox con valor preseleccionado
titulo_seleccionado = st.sidebar.selectbox("Tema de conversación actual", list(opciones.keys()), index=list(opciones.keys()).index(titulo_actual))

# Actualizar la selección en sesión
st.session_state.selector_temp_choice = opciones[titulo_seleccionado]
#------
folder = st.session_state.selector_temp_choice
st.sidebar.markdown("""
<div style="background-color: rgba(61, 157, 243, 0.2); padding: 1rem; border-radius: 6px; font-size: 0.92rem;margin-top: 0.5rem;">
Puedes visitar nuestra página oficial <a href="https://vallegrande.edu.pe/" target="_blank">aquí</a>.
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown(" ")
if st.sidebar.button("Nueva conversación"):
    st.session_state.memory = ConversationalMemory()
    st.session_state.chat_history = []
    st.session_state.partial_response = ""
    st.session_state.selected_filename = None
    st.session_state.auto_intro_done = False
    st.session_state.recent_interactions = deque(maxlen=3)
    st.session_state.selector_temp_choice = None
    st.session_state.last_summary = ""
    st.session_state.last_user_query = ""
    st.rerun()

st.sidebar.markdown("""
<div style="margin-top: -1.5rem;">
<hr style="border: 1px solid #444;" />
</div>
""", unsafe_allow_html=True)

st.sidebar.caption("© Valle Grande 2025")


# === RESPUESTA INICIAL AUTOMÁTICA ===
if not st.session_state.auto_intro_done:
    intro_question = "por favor presentate de manera educada y respetuosa, ademas preguntame en que me puedes ayudar, aun no uses referencias (si existe usa el indice.pdf)"
    pdf_relevante = seleccionar_pdf_relevante(intro_question, folder, api_key)
    json_path = f"{folder}/{Path(pdf_relevante).stem}.json"
    time.sleep(0.6)

    st.session_state.selected_filename = json_path
    results = hybrid_search(intro_question, st.session_state.selected_filename, model_path=model_path, limit=6)

    response_accum = []
    def capture(token):
        response_accum.append(token)

    generate_answer_streaming(intro_question, results, api_key, on_token_callback=capture)
    full_response = "".join(response_accum)

    st.session_state.chat_history.append(("Asistente", full_response, assistant_avatar))
    st.session_state.auto_intro_done = True

# MOSTRAR HISTORIAL
for entry in st.session_state.chat_history:
    if len(entry) == 3:
        sender, message, avatar = entry
    else:
        sender, message = entry
        avatar = None
    with st.chat_message("user" if sender == "Tú" else "assistant", avatar=avatar):
        st.markdown(message)
    #time.sleep(0.6)

# ENTRADA DE USUARIO
user_query = st.chat_input("Escribe tu pregunta...")

if user_query:

    with st.chat_message("user"):
        st.markdown(user_query)

    query_with_context = (
        f"Este es el contexto de la conversación: {st.session_state.last_summary}\n\n"
        f"La última pregunta fue: {st.session_state.last_user_query}\n"
        f"Se respondió usando el PDF: {Path(st.session_state.selected_filename).name}\n\n"
        f"Pregunta actual: {user_query}"
    )
    pdf_relevante = seleccionar_pdf_relevante(query_with_context, folder, api_key)

    json_path = f"{folder}/{Path(pdf_relevante).stem}.json"

    # Mostrar aviso si cambió el documento
    if st.session_state.selected_filename != json_path:
        aviso = f"📂 Documento actualizado: **{pdf_relevante}**"
        st.session_state.chat_history.append(("Asistente", aviso, assistant_avatar))
        st.caption(aviso)

    st.session_state.selected_filename = json_path

    # Búsqueda híbrida
    results = hybrid_search(user_query, st.session_state.selected_filename, model_path=model_path, limit=5)

    # Mostrar respuesta con streaming
    with st.chat_message("assistant", avatar=assistant_avatar):
        spinner = st.empty()
        response_placeholder = st.empty()
        st.session_state.partial_response = ""

        def update_response(token):
            st.session_state.partial_response += token
            response_placeholder.markdown(st.session_state.partial_response)

        with spinner.container():
            with st.spinner("Generando respuesta..."):
                history_text = "\n\n".join(st.session_state.recent_interactions)

                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": f"Resume en pocas líneas las siguientes interacciones:\n{history_text}"}],
                    temperature=0
                )
                st.session_state.last_summary = completion.choices[0].message.content.strip()
                prompt_con_memoria = f"Resumen de la conversación previa:\n{st.session_state.last_summary}\n\nUsuario: {user_query}."

                generate_answer_streaming(
                    prompt_con_memoria,
                    results,
                    api_key,
                    on_token_callback=update_response
                )
        spinner.empty()


    # Guardar historial
    st.session_state.recent_interactions.append(f"Usuario: {user_query}\nAsistente: {st.session_state.partial_response}")
    st.session_state.chat_history.append(("Tú", user_query))
    st.session_state.chat_history.append(("Asistente", st.session_state.partial_response, assistant_avatar))
    st.session_state.last_user_query = user_query