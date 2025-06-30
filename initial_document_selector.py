import streamlit as st
import json
import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def inject_custom_css(css_path="assets/custom_styles.css"):
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_initial_selector(catalog_path="catalog/document_catalog.json"):
    inject_custom_css()

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    if "selector_temp_choice" not in st.session_state:
        st.session_state.selector_temp_choice = None
    if "show_all_documents" not in st.session_state:
        st.session_state.show_all_documents = False

    logo_base64 = get_image_base64("assets/logo_vallegrancito.png")

    # Cabecera
    st.markdown(f"""
    <div class="vallegrancito-header">
        <div class="vallegrancito-logo-container">
            <img src="data:image/png;base64,{logo_base64}" style="height: 25px; width: 25px;" />
        </div>
        <div class="vallegrancito-title">
            Vallegrancito
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mensaje de bienvenida
    st.markdown("""
    <div class="vallegrancito-description fade-slide">
        ¡Hola! Soy tu asistente virtual. Puedo ayudarte a encontrar información sobre carreras, mallas curriculares y más. 
        <br><br>Elige una carpeta temática para comenzar.
    </div>
    """, unsafe_allow_html=True)

    # Documentos
    visible_docs = catalog[:3]
    hidden_docs = catalog[3:]
    if st.session_state.show_all_documents:
        visible_docs += hidden_docs

    for doc in visible_docs:
        title = doc["title"]
        with st.container():
            cols = st.columns([0.95, 0.05])
            with cols[0]:
                if st.button(f"{title}", key=f"btn_{title}"):
                    st.session_state.selector_temp_choice = doc["filename"]
                    st.session_state.intro_question = "por favor presentate de manera educada y respetuosa, ademas preguntame en que me puedes ayudar, aun no uses referencias (si existe usa el indice.pdf)"
                    st.rerun()

                st.markdown(f"""
                <div class="vallegrancito-card fade-slide">
                    {doc['description']}
                </div>
                """, unsafe_allow_html=True)

    if hidden_docs:
        label = " Ver más" if not st.session_state.show_all_documents else " Ver menos"
        cols = st.columns([0.8, 0.2])
        with cols[1]:
            if st.button(label):
                st.session_state.show_all_documents = not st.session_state.show_all_documents
                st.rerun()
