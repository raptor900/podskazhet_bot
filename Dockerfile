FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot/ ./bot/

# Create directories for knowledge base and user queries
RUN mkdir -p /app/knowledge_base /app/user_queries /app/chroma_db

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "-m", "bot.main"]
