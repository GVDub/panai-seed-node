from sentence_transformers import SentenceTransformer

# Load all-mpnet-base-v2 model for embedding (768-dimension)
embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embed_text(text: str) -> list:
    try:
        vector = embed_model.encode(text, normalize_embeddings=True).tolist()
        if not vector or len(vector) != 768:
            print(f"[Embedding ERROR] Invalid vector — len={len(vector) if vector else 'None'} — text='{text[:50]}'")
        else:
            print(f"[Embedding OK] Vector len={len(vector)} for text: '{text[:50]}'")
        return vector
    except Exception as e:
        print(f"[Embedding EXCEPTION] Failed to embed: {text[:50]} — {e}")
        return None