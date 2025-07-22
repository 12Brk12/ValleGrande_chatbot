import json
import pathlib
from pydantic import BaseModel
from groq import Groq
import instructor

class MetadataSelection(BaseModel):
    pdf_relevante: str  # ← nombre del PDF relevante

def seleccionar_pdf_relevante(pregunta: str, metadata_folder: str, api_key: str) -> str:
    metadata_path = pathlib.Path(f"rag_ingested_chunks/{metadata_folder}/metadata_config.json")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadatas = json.load(f)

    # Construir resumen respetando orden original y mostrando group_note solo al aparecer
    resumen = ""
    last_group_note = None
    shown_notes = set()

    for nombre, meta in metadatas.items():
        group_note = meta.get("group_note")
        if group_note and group_note not in shown_notes:
            resumen += f"\n🧩 Observación: {group_note}\n\n"
            shown_notes.add(group_note)

        indent_level = int(meta.get("indent_level", 0))
        base_indent = "  " * indent_level
        bullet_indent = "  " * (indent_level + 1)

        resumen += f"{base_indent}- {meta.get('document_title', 'Sin título')} ({nombre}):\n"
        for tag in meta.get("tags", []):
            resumen += f"{bullet_indent}• {tag}\n"

    prompt = f"""Tengo la siguiente pregunta junto con un contexto previo:

{pregunta}

Devuélveme **solo el nombre exacto de un único PDF** que sea el más relevante para responder esta pregunta.
Si consideras que la pregunta no tiene mucho sentido, ten en cuenta cuál fue el anterior PDF.
Sin embargo lo más importante es que el PDF que selecciones **SIEMPRE** debe ser uno de estos:
{resumen}

Tu respuesta debe estar en este formato JSON:
{{ "pdf_relevante": "nombre_del_archivo.pdf" }}
"""

    client = instructor.patch(Groq(api_key=api_key))

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=MetadataSelection,
            messages=[{"role": "user", "content": prompt}],
            max_retries=2,
            temperature=0
        )
        return response.pdf_relevante
    except Exception as e:
        print(f"❌ Error al seleccionar PDF relevante: {e}")
        return ""
