import faiss
import os
import pickle

INDEX_PATH = "vectorstore/faiss.index"
CHUNKS_PATH = "vectorstore/chunks.pkl"

dimension = 384

def create_new_index():
    return faiss.IndexFlatL2(dimension)

# Load or create index
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = create_new_index()

def reset_index():
    global index
    index = create_new_index()

    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)

    if os.path.exists(CHUNKS_PATH):
        os.remove(CHUNKS_PATH)

def save_index():
    faiss.write_index(index, INDEX_PATH)

def save_chunks(chunks):
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

def load_chunks():
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "rb") as f:
            return pickle.load(f)
    return []

def search(query_embedding, doc_id=None, top_k=10):
    if index.ntotal == 0:
        return []

    D, I = index.search(query_embedding, top_k)
    chunks = load_chunks()

    results = []

    for i in I[0]:
        if i >= len(chunks):
            continue

        chunk = chunks[i]

        if doc_id:
            if chunk["doc_id"].strip().lower() != doc_id.strip().lower():
                continue

        results.append(chunk["text"])

    return results