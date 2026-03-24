import re
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from groq import Groq

from app.db.vector_store import index, save_index, save_chunks, load_chunks, search, reset_index
from app.services.embedding_service import get_embeddings
from app.core.config import GROQ_API_KEY

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(api_key=GROQ_API_KEY)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def read_file(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def process_document(file_path, doc_id):
    reset_index()
    save_chunks([])

    text = read_file(file_path)

    if not text:
        return "No readable content found"

    chunks = chunk_text(text)

    chunks_with_meta = [
        {"text": chunk, "doc_id": doc_id}
        for chunk in chunks
    ]

    embeddings = get_embeddings([c["text"] for c in chunks_with_meta])

    index.add(embeddings)

    save_chunks(chunks_with_meta)
    save_index()

    return f"{len(chunks)} chunks added"


def query_rag(query, history=None, doc_id=None):
    all_chunks = load_chunks()

    # 🔥 FILTER (safe match)
    if doc_id:
        filtered = [
            c for c in all_chunks
            if c["doc_id"].strip().lower() == doc_id.strip().lower()
        ]
        if filtered:
            all_chunks = filtered

    if not all_chunks:
        return "No document found. Please upload a document first."

    # 🔥 SUMMARY MODE
    if "summary" in query.lower() or "summarize" in query.lower():
        context = "\n\n".join([c["text"] for c in all_chunks[:20]])

    else:
        # 🔥 MAIN SEARCH
        query_embedding = model.encode([query])
        results = search(query_embedding, doc_id)

        # 🔥 FALLBACK (IMPORTANT FIX)
        if not results:
            print("⚠️ No search results → using fallback chunks")
            results = [c["text"] for c in all_chunks[:5]]

        context = "\n\n".join(results)

    if not context:
        return "I couldn't find relevant information in the document."

    # 🔥 IMPROVED PROMPT
    prompt = f"""
You are a helpful AI assistant.

Answer using the context below.

Rules:
- Keep answer simple
- Be direct
- If partial info is available, still answer

Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content