import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DOC_PATHS = [
    r"C:\Users\HP\Desktop\Retail-Agent\AI-Assignment-Project\docs\catalog.md",
    r"C:\Users\HP\Desktop\Retail-Agent\AI-Assignment-Project\docs\kpi_definitions.md",
    r"C:\Users\HP\Desktop\Retail-Agent\AI-Assignment-Project\docs\marketing_calendar.md",
    r"C:\Users\HP\Desktop\Retail-Agent\AI-Assignment-Project\docs\product_policy.md"
]



def chunk_text(text: str, chunk_size: int = 250):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]



def load_docs_from_paths(file_paths, chunk_size=250):
    documents = []
    metadata = []

    for path in file_paths:
        if not os.path.exists(path):
            print(f"[WARNING] File not found: {path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text, chunk_size)

        file = os.path.basename(path)
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadata.append({
                "source": file,
                "chunk_id": f"{file}::chunk{i}"
            })

    return documents, metadata


#vectors
def build_tfidf_index(docs):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(docs)
    return vectorizer, vectors



#retrivers
def retrieve(query, top_k, vectorizer, doc_vectors, docs, metadata):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, doc_vectors)[0]

    top_ids = scores.argsort()[-top_k:][::-1]

    return [
        {
            "text": docs[i],
            "score": float(scores[i]),
            "source": metadata[i]["source"],
            "chunk_id": metadata[i]["chunk_id"]
        }
        for i in top_ids
    ]



#pipeline
def init_retriever(chunk_size=250):
    docs, metadata = load_docs_from_paths(DOC_PATHS, chunk_size)
    vectorizer, vectors = build_tfidf_index(docs)
    return docs, metadata, vectorizer, vectors


#Test
if __name__ == "__main__":
    print("Building TF-IDF RAG Retriever...")
    docs, meta, vect, vecs = init_retriever()
    print(f"Loaded documents: {len(docs)} chunks")
    query = "What is the Summer Spice Campaign start date?"
    results = retrieve(query, 3, vect, vecs, docs, meta)
    for r in results:
        print("\n--- RESULT ---")
        print("Score:", r["score"])
        print("Source:", r["source"])
        print("Chunk:", r["chunk_id"])
        print("Text:", r["text"][:200], "...")
