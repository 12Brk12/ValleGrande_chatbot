import streamlit as st
import json
import os
from streamlit_option_menu import option_menu

def load_custom_styles():
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """, unsafe_allow_html=True)
    css_path = "assets/custom_styles.css"
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_book_categories(metadata_path="metadata_summary/summary_metadata.json"):
    load_custom_styles()

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            all_books = json.load(f)
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo de metadata.")
        return

    topics = sorted({info.get("topic", "Sin categoría") for info in all_books.values()})

    st.markdown("""
        <div style='margin-top: -3.25rem; margin-bottom: 1rem; padding: 0rem;'>
            <div class="fade-slide" style='display: flex; align-items: center; gap: 0.6rem;'>
                <i class="fa-solid fa-book-open" style="color: white; font-size: 1.5rem;"></i>
                <h3 style='color: white; margin: 0;'>Libros Digitales</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="fade-slide book-card">
            <p>
                Nuestra biblioteca institucional cuenta con una <strong>selección de libros electrónicos</strong> disponibles para <strong>estudiantes, docentes e investigadores</strong>.<br><br>
                Además, puedes <strong>conversar con una IA</strong> que te orientará según el contenido de cada libro.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- Menú horizontal con streamlit-option-menu ---
    selected = option_menu(
        menu_title=None,
        options=["Todos", "Buscar", "Filtrar"],
        icons=["book", "search", "funnel"],
        orientation="horizontal",
        default_index=0
    )

    # Variables locales para búsqueda y categoría
    search_term = ""
    selected_topics = []

    # Entrada según modo
    if selected == "Buscar":
        search_term = st.text_input(
            "Escribe parte del título del libro",
            placeholder="Ejemplo: Kali Linux"
        )
        selected_topics = []

    elif selected == "Filtrar":
        selected_topics = st.multiselect(
            "Selecciona una o varias categorías",
            topics,
            placeholder="Selecciona una categoría"
        )
        search_term = ""

    # En modo Todos también se aplican sin filtros
    filtered_books = {
        title: info for title, info in all_books.items()
        if (selected != "Filtrar" or not selected_topics or info.get("topic", "Sin categoría") in selected_topics)
           and (search_term.lower() in title.lower())
    }

    if not filtered_books:
        st.info("No se encontraron libros con esos filtros.")
        return

    # --- Agrupar por categoría ---
    grouped = {}
    for title, info in filtered_books.items():
        topic = info.get("topic", "Sin categoría")
        grouped.setdefault(topic, []).append((title, info))

    for topic, books in grouped.items():
        st.markdown(f"""
            <h4 class="fade-slide" style="margin: .5rem 0">
                Categoría <strong><span style="border-bottom: 4px solid #FF4B4B;">{topic}</span> ({len(books)})</strong>
            </h4>
        """, unsafe_allow_html=True)

        for title, info in books:
            main_folder = info.get("main_folder", "")
            author = info.get("author", "Desconocido")
            reference_url = info.get("reference_url", "#")


            with st.expander(f"# {title}", expanded=False):
                col1, col2, col3= st.columns([1.9, 1.1,1.1])
                with col1:
                    st.markdown(f"""
                        <div style='margin-bottom: -1rem;'>
                            <strong>Autor:</strong> {author}
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                        <div style= 'margin-bottom: .5rem;'>
                            <a href="{reference_url}" target="_blank" class="link-button col-download">
                                Descargar guía (PDF)
                            </a>
                        </div>
                    """, unsafe_allow_html=True)

                with col3:
                    if st.button("💬 Habla con la IA", key=f"btn_{main_folder}"):
                        st.session_state.selector_temp_choice = f"{main_folder}/Table_of_contents"
                        st.session_state.intro_question = (
                            "Dime de manera detallada **qué información que tienes** "
                            "(si existe usa el table_of_contents.pdf) "
                            "Presentate con un: Hola soy ..."
                        )
                        st.rerun()