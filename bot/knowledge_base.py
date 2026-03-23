import os
from typing import List, Dict, Any

from bot.config import Config
from bot.embeddings import EmbeddingManager
from bot.llm import LLMManager
from bot.utils import chunk_text, count_tokens


class KnowledgeBaseManager:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.llm_manager = LLMManager()
        self.kb_path = Config.KNOWLEDGE_BASE_PATH

    def load_all_documents(self) -> str:
        """Load all text from knowledge base"""
        all_text = []

        for root, dirs, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith(('.txt', '.md')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        all_text.append(f"\n\n--- Source: {file_path} ---\n\n{content}")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

        return "\n".join(all_text)

    def answer_question(self, question: str) -> tuple:
        """Answer question using knowledge base"""
        # Check if knowledge base exists
        if not os.path.exists(self.kb_path) or not os.listdir(self.kb_path):
            return "База знаний пуста. Пожалуйста, добавьте документы в папку knowledge_base.", []

        # Load all documents
        all_docs = self.load_all_documents()

        # Decide if we need embeddings
        if self.llm_manager.should_use_embeddings(all_docs):
            # Use embeddings for RAG
            relevant_chunks = self.embedding_manager.search(question, k=5)
            context = [chunk[0] for chunk in relevant_chunks]
            sources = [chunk[1].get('source', 'Unknown') for chunk in relevant_chunks]
        else:
            # Put everything in context
            context = [all_docs]
            sources = ["Full knowledge base"]

        if not context:
            return "В базе знаний нет информации по вашему вопросу.", []

        # Get response from LLM
        answer, sources = self.llm_manager.get_response(question, context)

        return answer, sources

    def rebuild_index(self):
        """Rebuild the embedding index"""
        self.embedding_manager.rebuild_index(self.kb_path)
