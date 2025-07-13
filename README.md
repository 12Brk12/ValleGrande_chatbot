# Vallegrancito Chatbot

Vallegrancito es un asistente conversacional construido con Streamlit que realiza **búsquedas híbridas** sobre documentos locales y genera respuestas con los modelos de Groq. El proyecto está orientado a uso académico dentro de Valle Grande.

## Estructura del repositorio

```
assets/                # imágenes y estilos CSS
catalog/               # catálogo de documentos disponibles para el chat
chatbot.py             # interfaz de chat en Streamlit
hybrid_search.py       # búsqueda textual y vectorial combinada
generate_answer_2.py   # generación de respuestas con Groq
streamlit_app.py       # aplicación principal de navegación
rag_documents_ingestion.py # script para procesar PDFs
rag_ingested_chunks/   # chunks y embeddings generados
requirements.txt       # dependencias de Python
```

Los documentos originales (PDF) y sus metadatos se encuentran bajo `data/`. Cada carpeta de `data/` contiene un `metadata_config.json` con el título, etiquetas y enlace de referencia del documento.

## Instalación

1. Crea un entorno virtual y actívalo:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Coloca tu clave de Groq en `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "tu_clave_aqui"
```

## Preparar los documentos

Antes de usar el chatbot es necesario convertir los PDFs en bloques con sus embeddings:

```bash
python rag_documents_ingestion.py
```

Esto creará archivos JSON dentro de `rag_ingested_chunks/` que luego se usan para la búsqueda híbrida.

## Ejecutar la aplicación

Con todo configurado, inicia la interfaz de Streamlit:

```bash
streamlit run streamlit_app.py
```

Al abrir la aplicación podrás elegir un tema de documentos y conversar con Vallegrancito. Las preguntas se responden utilizando los textos encontrados y manteniendo las referencias de cada fuente.

## Próximos pasos

- Explora `hybrid_search.py` para entender cómo se combinan los resultados de busqueda textual (Lunr) y vectorial (embeddings).
- Revisa `generate_answer_2.py` para ver cómo se envían las consultas al modelo de Groq y se recibe la respuesta en streaming.
- Personaliza los documentos en `data/` y actualiza el catálogo en `catalog/document_catalog.json` según tus necesidades.

¡Esperamos que Vallegrancito sea de gran ayuda!
