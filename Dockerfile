FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot/ ./bot/
COPY .env ./

# Create directories for knowledge base and user queries
RUN mkdir -p /app/knowledge_base /app/user_queries

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "-m", "bot.main"]
