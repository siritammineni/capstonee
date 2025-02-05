from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os, shutil

AZURE_OPENAI_API_KEY = "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"  
AZURE_OPENAI_ENDPOINT = "https://models.inference.ai.azure.com"  
AZURE_EMBEDDING_MODEL = "text-embedding-3-small" 

def create_vector_store(chunks, metadatas=None, clear_existing=False):
    if clear_existing:
        if os.path.exists("faiss_index"):
            shutil.rmtree("faiss_index")  
    if not chunks:
        raise ValueError("No chunks present")
    embeddings = OpenAIEmbeddings(
        model=AZURE_EMBEDDING_MODEL, 
        openai_api_key=AZURE_OPENAI_API_KEY,
        openai_api_base=AZURE_OPENAI_ENDPOINT
    )
    if metadatas is None or len(metadatas) != len(chunks):
        print("Metadata was missing or incorrect length, initializing default metadata...")
        metadatas = [{"source": "Unknown Document"}] * len(chunks) 

    vector_store = FAISS.from_texts(chunks, embeddings, metadatas=metadatas) 
    vector_store.save_local("faiss index")
    return vector_store

