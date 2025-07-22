import json
import pathlib
import shutil
import fitz  # PyMuPDF
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# === EMBEDDINGS ===
model_dir = pathlib.Path(
    "huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf")
embedder = HuggingFaceEmbeddings(model_name=str(model_dir))


def extract_clean_text(pdf_path):
    """Extrae texto completo de un PDF sin errores de fragmentación."""
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text("text") + "\n"
    return all_text


def process_folder(folder_name: str, subfolder: str):
    data_root = pathlib.Path("data")
    input_folder = data_root / folder_name / subfolder
    output_folder = pathlib.Path("rag_ingested_chunks") / folder_name / subfolder
    output_folder.mkdir(parents=True, exist_ok=True)

    # === CARGAR METADATA LOCAL
    metadata_path = input_folder / "metadata_config.json"
    with open(metadata_path, "r", encoding="utf-8") as f:
        local_metadata = json.load(f)

    print(f"📁 Procesando carpeta: {folder_name}/{subfolder}")
    for file in input_folder.iterdir():
        if file.suffix.lower() == ".pdf":
            config = local_metadata.get(file.name)
            if not config:
                print(f"⚠️ No hay metadata para {file.name}, omitido.")
                continue

            print(f"➡️ Procesando {file.name}")
            raw_text = extract_clean_text(file)

            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=500, chunk_overlap=125
            )
            texts = splitter.create_documents([raw_text])

            file_chunks = []
            for i, doc in enumerate(texts):
                chunk = {
                    "id": f"{file.stem}-{i + 1}",
                    "text": doc.page_content,
                    "embedding": embedder.embed_query(doc.page_content),
                    "source_pdf": file.name,
                    "reference_url": config.get("reference_url", "")
                }
                file_chunks.append(chunk)

            output_path = output_folder / f"{file.stem}.json"
            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(file_chunks, f_out, indent=4)

            print(f"✅ {file.name} guardado en {output_path}")

        elif file.is_file() and file.suffix.lower() != ".pdf":
            destination = output_folder / file.name
            shutil.copy(file, destination)
            print(f"📄 Archivo no PDF copiado: {file.name}")


# === USO DIRECTO ===
if __name__ == "__main__":
    process_folder("Mastering_Linux_Administration", "Table_of_contents")
