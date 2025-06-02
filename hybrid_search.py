import json
import numpy as np
from lunr import lunr
from sklearn.metrics.pairwise import cosine_similarity
from langchain_huggingface import HuggingFaceEmbeddings


def load_document(filename, base_dir="rag_ingested_chunks"):
    with open(f"{base_dir}/{filename}", "r") as f:
        return json.load(f)


def build_lunr_index(documents):
    return lunr(ref="id", fields=["text"], documents=documents)


def full_text_search(query, index, documents_by_id, limit):
    # 🧼 Limpiar la consulta para evitar errores de parsing
    safe_query = query.replace(":", " ").replace("\"", "").replace("'", "")
    # Aquí se hace la búsqueda ya limpia
    results = index.search(safe_query)
    return [documents_by_id[r["ref"]] for r in results[:limit]]


def vector_search(query, documents, embeddings, embedder, limit):
    query_embedding = embedder.embed_query(query)
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    top_indices = similarities.argsort()[-limit:][::-1]
    return [documents[i] for i in top_indices]


def reciprocal_rank_fusion(text_results, vector_results, k=60):
    scores = {}
    for i, doc in enumerate(text_results):
        scores[doc["id"]] = scores.get(doc["id"], 0) + 1 / (i + k)
    for i, doc in enumerate(vector_results):
        scores[doc["id"]] = scores.get(doc["id"], 0) + 1 / (i + k)
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs


def hybrid_search(user_query, selected_filename, model_path, limit=6):
    documents = load_document(selected_filename)
    documents_by_id = {doc["id"]: doc for doc in documents}
    embedder = HuggingFaceEmbeddings(model_name=str(model_path))

    # Preprocesamiento
    index = build_lunr_index(documents)
    embeddings = np.array([doc["embedding"] for doc in documents])

    # Búsquedas
    text_results = full_text_search(user_query, index, documents_by_id, limit * 2)
    vector_results = vector_search(user_query, documents, embeddings, embedder, limit * 2)
    fused_ids = reciprocal_rank_fusion(text_results, vector_results)

    return [documents_by_id[doc_id] for doc_id, _ in fused_ids[:limit]]
