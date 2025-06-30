import json
import pathlib
import pymupdf4llm
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# === CONFIGURACIÓN ===
target_folder_name = "UltimateLinuxNewbieGuide/Intro"  # Carpeta a procesar

data_root = pathlib.Path("data")
input_folder = data_root / target_folder_name
output_folder = pathlib.Path("rag_ingested_chunks") / target_folder_name
output_folder.mkdir(parents=True, exist_ok=True)

# === CARGAR METADATA LOCAL (solo para reference_url)
metadata_path = input_folder / "metadata_config.json"
with open(metadata_path, "r", encoding="utf-8") as f:
    local_metadata = json.load(f)

# === EMBEDDINGS ===
model_dir = pathlib.Path("huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf")
embedder = HuggingFaceEmbeddings(model_name=str(model_dir))

# === PROCESAR PDFS
print(f"📁 Procesando carpeta: {target_folder_name}")
for pdf_file in input_folder.glob("*.pdf"):
    config = local_metadata.get(pdf_file.name)
    if not config:
        print(f"⚠️ No hay metadata para {pdf_file.name}, omitido.")
        continue

    print(f"➡️ Procesando {pdf_file.name}")
    md_text = pymupdf4llm.to_markdown(pdf_file)

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=125
    )
    texts = splitter.create_documents([md_text])

    file_chunks = []
    for i, doc in enumerate(texts):
        chunk = {
            "id": f"{pdf_file.stem}-{i + 1}",
            "text": doc.page_content,
            "embedding": embedder.embed_query(doc.page_content),
            "source_pdf": pdf_file.name,
            "reference_url": config.get("reference_url", "")
        }
        file_chunks.append(chunk)

    # Guardar chunks en archivo JSON
    output_path = output_folder / f"{pdf_file.stem}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(file_chunks, f, indent=4)

    print(f"✅ {pdf_file.name} guardado en {output_path}")
