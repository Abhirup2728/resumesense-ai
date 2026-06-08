"""
ResumeSense AI - Embedder & Vector Store
Custom chunking + Gemini embeddings + ChromaDB storage.
"""

import os
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma   # <-- FIXED import

# Persistent ChromaDB directory
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

def get_embeddings_model():
    """Return the Gemini embedding model instance."""
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    """
    Split text into overlapping chunks without external libraries.
    Tries to break on sentence boundaries.
    """
    # Normalise whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Simple sentence splitting on ., !, ? followed by space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(sentence) > chunk_size:
                words = sentence.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= chunk_size:
                        current_chunk = (current_chunk + " " + word).strip()
                    else:
                        chunks.append(current_chunk)
                        current_chunk = word
            else:
                current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Apply overlap (simple approach)
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_words = overlapped[-1].split()
            curr_words = chunks[i].split()
            overlap_text = ""
            for w in reversed(prev_words):
                if len(overlap_text) + len(w) + 1 <= chunk_overlap:
                    overlap_text = w + " " + overlap_text
                else:
                    break
            overlap_text = overlap_text.strip()
            if overlap_text:
                overlapped.append(overlap_text + " " + chunks[i])
            else:
                overlapped.append(chunks[i])
        chunks = overlapped
    
    return chunks

def create_vector_store(text_chunks: list, collection_name: str = "resume") -> Chroma:
    """
    Create a ChromaDB vector store from a list of text chunks.
    """
    embeddings = get_embeddings_model()
    vector_store = Chroma.from_texts(
        texts=text_chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_DB_PATH
    )
    vector_store.persist()
    print(f"Vector store created with {len(text_chunks)} chunks in collection '{collection_name}'")
    return vector_store

def load_vector_store(collection_name: str = "resume") -> Chroma:
    """Load an existing ChromaDB vector store from disk."""
    embeddings = get_embeddings_model()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

if __name__ == "__main__":
    sample_text = """
    John Doe is a Data Scientist with 5 years of experience.
    He has expertise in Python, machine learning, SQL, and AWS.
    He built customer churn prediction models and deployed them using Docker.
    """
    chunks = split_text(sample_text)
    print(f"Split into {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}: {chunk[:80]}...")
    
    store = create_vector_store(chunks, collection_name="test_resume")
    print("Test successful!")
