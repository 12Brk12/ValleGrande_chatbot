import json
import pathlib
from pydantic import BaseModel
from groq import Groq
import instructor


class MetadataSelection(BaseModel):
    pdf_relevante: str  # ← nombre del PDF relevante


def seleccionar_pdf_relevante(pregunta: str, metadata_folder: str, api_key: str) -> str:
    metadata_path = pathlib.Path(f"data/{metadata_folder}/metadata_config.json")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadatas = json.load(f)

    resumen = ""
    for nombre, meta in metadatas.items():
        resumen += f"- {meta['document_title']} ({nombre}):\n"
        for tag in meta["tags"]:
            resumen += f"  • {tag}\n"

    prompt = f"""Tengo la siguiente pregunta:

{pregunta}

Y un resumen de documentos con sus títulos y temas clave. 
Devuélveme **solo el nombre exacto de un único PDF** que sea el más relevante para responder esta pregunta.
Si consideras que la pregunta no tiene mucho sentido, ten en cuenta cual cue fue el anterior pdf.
 
Tu respuesta debe estar en este formato JSON:
{{ "pdf_relevante": "nombre_del_archivo.pdf" }}

El PDF que selecciones debe ser uno de estos:
Resumen:
{resumen}
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
