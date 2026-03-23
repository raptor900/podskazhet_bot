import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # OpenRouter
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_EMBEDDING_MODEL = os.getenv('OPENROUTER_EMBEDDING_MODEL', 'openai/text-embedding-3-large')
    OPENROUTER_LLM_MODEL = os.getenv('OPENROUTER_LLM_MODEL', 'stepfun/step-3.5-flash:free')

    # RAG settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
    MAX_CONTEXT_TOKENS = int(os.getenv('MAX_CONTEXT_TOKENS', 8000))

    # Paths
    KNOWLEDGE_BASE_PATH = '/app/knowledge_base'
    USER_QUERIES_PATH = '/app/user_queries'
    CHROMA_DB_PATH = '/app/chroma_db'
