import streamlit as st
import json
from collections import deque
from streamlit_option_menu import option_menu
from base64 import b64encode
from initial_document_selector import show_initial_selector
from ulng import show_ulng
from book_category_viewer import show_book_categories
from chatbot import show_chatbot

# === CONFIGURACIÓN INICIAL ===
st.set_page_config(page_title="Vallegrancito", page_icon="assets/page_icon.jpg")

# === FUNCIÓN PARA LOGO EN SIDEBAR ===
def mostrar_logo_sidebar(image_path="assets/logo_completo.png"):
    with open(image_path, "rb") as img_file:
        encoded = b64encode(img_file.read()).decode()
    st.sidebar.markdown(f"""
    <div style="text-align: center; margin-bottom: -1.5rem;">
        <img src="data:image/png;base64,{encoded}" width="230" />
    </div>
    """, unsafe_allow_html=True)

def load_document_selector_sidebar(catalog_path: str):
    """
    Carga el catálogo desde el archivo indicado y muestra el selector en el sidebar.
    Actualiza automáticamente `st.session_state.selector_temp_choice`.

    Parámetros:
    - catalog_path (str): Ruta al archivo JSON del catálogo (por ejemplo: "data/document_catalog.json")
    """
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Crear mapeo de título ↔ filename
    title_to_filename = {item["title"]: item["filename"] for item in catalog}
    filename_to_title = {v: k for k, v in title_to_filename.items()}

    # Obtener selección actual
    current_title = filename_to_title.get(
        st.session_state.selector_temp_choice,
        list(title_to_filename.keys())[0]
    )

    # Mostrar selector
    selected_title = st.sidebar.selectbox(
        "Tema de conversación actual",
        list(title_to_filename.keys()),
        index=list(title_to_filename.keys()).index(current_title)
    )

    # Verificar cambio y forzar recarga si corresponde
    new_choice = title_to_filename[selected_title]
    if st.session_state.selector_temp_choice != new_choice:
        st.session_state.selector_temp_choice = new_choice
        st.rerun()

def load_subfolder_selector_sidebar(metadata_path: str):
    """
    Muestra un selector de subcarpetas basado en la selección actual del libro.
    Los nombres visibles se limpian de guiones bajos para mayor legibilidad.
    """
    with open(metadata_path, "r", encoding="utf-8") as f:
        books = json.load(f)

    # Determinar libro actualmente seleccionado
    for book_title, info in books.items():
        if info.get("main_folder") and st.session_state.selector_temp_choice.startswith(info["main_folder"]):
            subfolders = info.get("subfolders", [])
            base = info["main_folder"]
            break
    else:
        subfolders = []
        base = ""

    if not subfolders:
        return

    # Mapeo: Nombre visible → subcarpeta real
    display_map = {sf.replace("_", " "): sf for sf in subfolders}

    # Subcarpeta actual
    current_subfolder = st.session_state.selector_temp_choice.split("/")[-1]
    current_display = current_subfolder.replace("_", " ")

    # Selector visible
    selected_display = st.sidebar.selectbox(
        "Sección del libro",
        list(display_map.keys()),
        index=list(display_map.keys()).index(current_display) if current_display in display_map else 0
    )

    # Actualizar selector_temp_choice con el valor real
    selected_subfolder = display_map[selected_display]
    new_choice = f"{base}/{selected_subfolder}"

    if st.session_state.selector_temp_choice != new_choice:
        st.session_state.selector_temp_choice = new_choice
        st.rerun()


def reset_chat_session():
    """
    Reinicia la conversación completa y vuelve al selector inicial.
    """
    st.session_state.chat_history = []
    st.session_state.partial_response = ""
    st.session_state.selected_filename = None
    st.session_state.auto_intro_done = False
    st.session_state.recent_interactions = deque(maxlen=3)
    st.session_state.selector_temp_choice = None
    st.session_state.last_summary = ""
    st.session_state.last_user_query = ""



mostrar_logo_sidebar()
st.sidebar.markdown("---")

# === MENÚ DE NAVEGACIÓN ===
with st.sidebar:
    selected = option_menu(
        menu_title="",
        options=["Chatbot", "Libros", "ULNG","Acerca de"],
        icons=["chat-dots", "book", "terminal","info-circle"],
        default_index=0,
    )

# === RESETEAR VARIABLES AL CAMBIAR DE SECCIÓN ===
previous_section = st.session_state.get("last_section")
current_section = selected

if previous_section and previous_section != current_section:
    reset_chat_session()

st.session_state["last_section"] = current_section

# === LÓGICA DEL MENÚ ===
if selected == "Chatbot":
    #st.session_state.intro_question = "por favor presentate de manera educada y respetuosa, ademas preguntame en que me puedes ayudar, aun no uses referencias (si existe usa el indice.pdf)"
    # Muestra chatbot si ya hay carpeta elegida
    if st.session_state.get("selector_temp_choice"):
        load_document_selector_sidebar("catalog/document_catalog.json") # o "data/document_catalog.json"o "document_catalog.json"
        st.sidebar.markdown(" ")
        if st.sidebar.button("Nueva conversación"):
            reset_chat_session()
            st.rerun()
        show_chatbot()
    else:
        show_initial_selector()

elif selected == "Libros":
    if st.session_state.get("selector_temp_choice"):
        load_subfolder_selector_sidebar("metadata_summary/summary_metadata.json")

        st.sidebar.markdown(" ")
        if st.sidebar.button("Regresar"):
            reset_chat_session()
            st.rerun()
        show_chatbot()
    else:
        show_book_categories()

elif selected == "ULNG":
    # st.session_state.intro_question = "Dime de manera detallada **que informacion que tienes** (si existe usa el start_chat.pdf)"
    if st.session_state.get("selector_temp_choice"):
        if st.sidebar.button("Regresar"):
            reset_chat_session()
            st.rerun()
        show_chatbot()
    else:
        show_ulng()

elif selected == "Acerca de":
    st.markdown("## ℹ️ Acerca de")
    st.write("Este es un asistente conversacional académico desarrollado para Valle Grande.")
    st.markdown("Desarrollado con ❤️ por [Tu Nombre o Equipo].")

st.sidebar.markdown("""
    <div style="margin-top: -1.5rem;">
    <hr style="border: 1px solid #444;" />
    </div>
    """, unsafe_allow_html=True)

st.sidebar.caption("© Valle Grande 2025")