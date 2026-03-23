import os
from typing import List, Union
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from bot.config import Config
from bot.utils import chunk_text


class EmbeddingManager:
    def __init__(self):
        self.method = Config.EMBEDDING_METHOD
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP

        if self.method == 'openrouter':
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=Config.OPENROUTER_API_KEY,
            )
            self.model = Config.OPENROUTER_EMBEDDING_MODEL
        else:
            self.model = SentenceTransformer(Config.LOCAL_EMBEDDING_MODEL)

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=Config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        if self.method == 'openrouter':
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        else:
            return self.model.encode(text).tolist()

    def index_document(self, file_path: str, content: str):
        """Index a document by splitting into chunks and storing embeddings"""
        chunks = chunk_text(content, self.chunk_size, self.chunk_overlap)

        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{os.path.basename(file_path)}_{i}"
            ids.append(chunk_id)
            embeddings.append(self.get_embedding(chunk))
            metadatas.append({
                "source": file_path,
                "chunk": i
            })
            documents.append(chunk)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def search(self, query: str, k: int = 5) -> List[tuple]:
        """Search for relevant chunks"""
        query_embedding = self.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        # Return list of (document, metadata) tuples
        relevant_chunks = []
        if results['documents'] and results['metadatas']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                relevant_chunks.append((doc, meta))

        return relevant_chunks

    def rebuild_index(self, knowledge_base_path: str):
        """Rebuild the entire index from knowledge base files"""
        # Clear existing collection
        self.chroma_client.delete_collection("knowledge_base")
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

        # Index all files
        for root, dirs, files in os.walk(knowledge_base_path):
            for file in files:
                if file.endswith(('.txt', '.md', '.pdf')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.index_document(file_path, content)
                        print(f"Indexed: {file_path}")
                    except Exception as e:
                        print(f"Error indexing {file_path}: {e}")
