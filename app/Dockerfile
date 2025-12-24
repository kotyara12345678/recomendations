FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

COPY requirements.txt .

RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

ENV TYPESENSE_HOST=typesense
ENV TYPESENSE_API_KEY=typesense_key_here
ENV TYPESENSE_COLLECTION=issues
ENV EMBED_MODEL=all-MiniLM-L6-v2

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# http://localhost:8000/docs
# docker-compose up --build
