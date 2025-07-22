import streamlit as st

def inject_custom_css(css_path="assets/custom_styles.css"):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_ulng():
    inject_custom_css()
    #st.markdown("# The Ultimate Linux Newbie Guide")
    st.title("The Ultimate Linux Newbie Guide")
    st.markdown(" ")
    st.markdown(" ")
    col1, col2 = st.columns([4, 9])

    with col1:
        st.image("assets/ulng_cover.png", use_container_width=True)
        st.markdown("""
        <div style='text-align: center; margin-top: .5rem;margin-bottom: 1.2rem;'>
            <a href="https://drive.google.com/file/d/1W5noI2AexLfie5Eo0ZIM30XrXFeAYwXX/view?usp=drive_link"
               target="_blank" class="link-button">
               Descargar guía (PDF)
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="fade-slide description-card">
            <p><strong>The Ultimate Linux Newbie Guide (ULNG)</strong> es una guía reconocida desde 2001 por ayudar a personas a iniciarse en el mundo de Linux.  
            Está pensada tanto para principiantes como para usuarios con experiencia que desean aprender a instalar, usar y dominar Linux.</p>

        - Las principales distribuciones de Linux  
        - Cómo instalar Linux de forma gratuita  
        - Uso diario de Linux sin tecnicismos  
        - Alternativas al software privativo de Windows/macOS  
        - Tutoriales, tips, guías en video y secciones avanzadas para SysAdmins
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Estos son algunos temas clave del libro. Selecciona uno para consultarlo con la IA:")
    st.markdown(" ")
    if st.button("Introducción y Tabla de contenido"):
        st.session_state.selector_temp_choice = "UltimateLinuxNewbieGuide/Intro"
        st.session_state.intro_question = (
            "Dime de manera detallada **qué información que tienes** "
            "(si existe usa el start_chat.pdf)"
        )
        st.rerun()
    st.markdown(f"""
    <div class="vallegrancito-card fade-slide">
        Conoce de qué trata este libro, qué temas cubre y quién lo escribió. Esta sección incluye una introducción general, el índice temático y una breve presentación del autor.
    </div>
    """, unsafe_allow_html=True)

    if st.button("Capitulo 1: Que es Linux?"):
        st.session_state.selector_temp_choice = "UltimateLinuxNewbieGuide/Chapter1"
        st.session_state.intro_question = (
            "Contienes información del Capitulo 1: What is Linux"
            "Dime de manera detallada **qué información que tienes** "
            "(si existe usa el table_of_contents.pdf)"
        )
        st.rerun()
    st.markdown(f"""
    <div class="vallegrancito-card fade-slide">
        Conoce qué es Linux, cómo nació y en qué se diferencia de UNIX. Aprende qué es un sistema operativo, la historia de UNIX y cómo Linus Torvalds creó el núcleo de Linux como software libre.
    </div>


    """, unsafe_allow_html=True)

    if st.button("Capitulo 2: Porque Linux - Cuales son los beneficios?"):
        st.session_state.selector_temp_choice = "UltimateLinuxNewbieGuide/Chapter2"
        st.session_state.intro_question = (
            "Contienes información del Capítulo 2: Why Linux – What are the Benefits?"
            "Dime de manera detallada **qué información que tienes** "
            "(si existe usa el table_of_contents.pdf)"
        )
        st.rerun()
    st.markdown(f"""
    <div class="vallegrancito-card fade-slide">
        Descubre por qué elegir Linux: es gratuito, seguro, personalizable, funciona en equipos antiguos y es usado por empresas como Google y Amazon. Ideal para quienes buscan libertad y control.
    </div>

    
    """, unsafe_allow_html=True)

    if st.button("Prueba"):
        st.session_state.selector_temp_choice = "Mastering_Linux_Administration/Table_of_contents"
        st.session_state.intro_question = (
            "Dime de manera detallada **qué información que tienes** "
            "(si existe usa el table_of_contents.pdf)"
            "Presentate con un: Hola soy ..."
        )
        st.rerun()
    st.markdown(f"""
    <div class="vallegrancito-card fade-slide">
        Descubre por qué elegir Linux: es gratuito, seguro, personalizable, funciona en equipos antiguos y es usado por empresas como Google y Amazon. Ideal para quienes buscan libertad y control.
    </div>


    """, unsafe_allow_html=True)