FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        sqlalchemy \
        asyncpg \
        pydantic-settings \
        alembic \
        httpx \
        requests \
        python-dotenv \
        aiofiles \
        aiohttp \
        openai \
        python-multipart \
        pymupdf \
        psycopg2-binary

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "RAG_System.main:app", "--host", "0.0.0.0", "--port", "8000"]