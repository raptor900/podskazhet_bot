import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import tiktoken

from bot.config import Config


def save_user_query(user_id: int, username: str, question: str, answer: str, context_used: List[str]):
    """Save user query and response to file"""
    user_dir = Path(Config.USER_QUERIES_PATH) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = user_dir / f'{timestamp}.json'

    data = {
        'user_id': user_id,
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'answer': answer,
        'context_used': context_used
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def count_tokens(text: str, model: str = 'gpt-3.5-turbo') -> int:
    """Count tokens in text"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding('cl100k_base')

    return len(encoding.encode(text))


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def format_structured_response(answer: str, sources: List[str]) -> str:
    """Format the final response with sources"""
    response = f"📝 **Ответ:**\n\n{answer}\n\n"

    if sources:
        response += "📚 **Источники:**\n"
        for i, source in enumerate(sources[:5], 1):  # Limit to 5 sources
            response += f"{i}. {source}\n"

    return response
