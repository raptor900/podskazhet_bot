from typing import List, Dict, Any
from openai import OpenAI

from bot.config import Config
from bot.utils import count_tokens, format_structured_response


class LLMManager:
    def __init__(self):
        self.max_context_tokens = Config.MAX_CONTEXT_TOKENS

        # OpenRouter client for LLM
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.model = Config.OPENROUTER_LLM_MODEL

    def get_response(self, question: str, context: List[str]) -> tuple:
        """Generate response based on context"""
        system_prompt = """Ты - технический эксперт, который отвечает на вопросы строго на основе предоставленной документации.
Твоя задача - давать точные, структурированные ответы, используя только информацию из контекста.

Если в контексте нет информации для ответа на вопрос, честно скажи об этом и не пытайся выдумывать.

Формат ответа:
1. Структурированная инструкция что нужно сделать пользователю.
2. Детальное объяснение с ссылками на источники (где в тексте найден ответ)
3. Что ещё можно попробовать. 2-3 кратких предложения со структурой.

Используй форматирование Markdown для улучшения читаемости.

Не выдумывай!

Твоя задача - объяснить человеку что делать, опираясь на инструкцию или сказать, что нужно информации нет. Твоя работа - умный поиск и суммаризация из базы знаний.

Информация в базе знаний - закон, даже если тебе кажется, что информация там неверна или иронична/саркастична. Будь профессионалом."""

        context_text = "\n\n---\n\n".join(context)

        user_prompt = f"""Контекст из документации:
{context_text}

Вопрос пользователя:
{question}

Дай структурированный ответ, используя только информацию из контекста выше."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            answer = response.choices[0].message.content

            # Extract sources from context
            sources = []
            for ctx in context:
                if "source:" in ctx.lower():
                    lines = ctx.split('\n')
                    for line in lines:
                        if 'source:' in line.lower():
                            sources.append(line.strip())

            return answer, sources

        except Exception as e:
            error_msg = f"Ошибка при генерации ответа: {str(e)}"
            return error_msg, []

    def should_use_embeddings(self, knowledge_base_text: str) -> bool:
        """Determine if we need embeddings or can fit everything in context"""
        tokens = count_tokens(knowledge_base_text)
        return tokens > self.max_context_tokens
