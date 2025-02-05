import os
import time
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from readingfiles import read_files
from chunking import chunk_documents
from embedding import create_vector_store


FAISS_INDEX_PATH = "faiss index"
LAST_UPDATED_FILE = "faiss_last_updated.txt"
def get_last_updated_time():
   """Retrieve the last time FAISS was updated."""
   if os.path.exists(LAST_UPDATED_FILE):
       with open(LAST_UPDATED_FILE, "r") as f:
           return float(f.read().strip())  
   return 0  
def update_last_updated_time():
   """Update the FAISS last modified time."""
   with open(LAST_UPDATED_FILE, "w") as f:
       f.write(str(time.time()))  
def load_or_create_vector_store(directory):
   """Creates FAISS index if not found or updates it if new files are added."""
   last_updated = get_last_updated_time()
   file_paths = get_all_files(directory)
   new_files = [f for f in file_paths if os.path.getmtime(f) > last_updated]
   if os.path.exists(FAISS_INDEX_PATH):
       print("✅ Loading existing FAISS index...")
       vector_store = FAISS.load_local(
           FAISS_INDEX_PATH,
           OpenAIEmbeddings(model="text-embedding-3-small"),
           allow_dangerous_deserialization=True
       )
       if new_files:
           print(f"New files detected: {new_files}. Updating FAISS...")
           new_documents = []
           for file_path in new_files:
               docs = read_files(file_path)
               for doc in docs:
                   doc.metadata = {"source": file_path}  
               new_documents.extend(docs)
           new_chunks_with_metadata = []
           for doc in new_documents:
               chunks = chunk_documents([doc])  
               for chunk in chunks:
                   new_chunks_with_metadata.append((chunk, doc.metadata["source"]))
           vector_store.add_texts(
               [chunk for chunk, _ in new_chunks_with_metadata],
               metadatas=[{"source": source} for _, source in new_chunks_with_metadata]  
           )
           vector_store.save_local(FAISS_INDEX_PATH)  
           update_last_updated_time()  
           print("FAISS updated with new files.")
   else:
       print("FAISS index not found. Processing all files...")
       documents = []
       for file_path in file_paths:
           docs = read_files(file_path)
           for doc in docs:
               doc.metadata = {"source": file_path}  
           documents.extend(docs)
       chunks_with_metadata = []
       for doc in documents:
           chunks = chunk_documents([doc])  
           for chunk in chunks:
               chunks_with_metadata.append((chunk, doc.metadata["source"]))  
       vector_store = create_vector_store(
           [chunk for chunk, _ in chunks_with_metadata],  
           metadatas=[{"source": source} for _, source in chunks_with_metadata],  
           clear_existing=True
       )
       update_last_updated_time()  
       print(" New FAISS index created.")
   return vector_store
def get_all_files(directory):
   """Retrieve all file paths from the given directory."""
   file_paths = []
   for root, _, files in os.walk(directory):
       for file in files:
           file_paths.append(os.path.join(root, file))
   return file_paths
if __name__ == "__main__":
   directory_path = "scraped pages final"  
   load_or_create_vector_store(directory_path)
   print(" Knowledge base setup complete. FAISS index is ready.")