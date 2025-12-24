FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY requirements.txt ./

RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt \
 || /root/.local/bin/uv pip install --system --no-cache -r requirements.txt \
 || uv pip install --system --no-cache -r requirements.txt

COPY . .

ENV TYPESENSE_HOST=typesense \
    TYPESENSE_API_KEY=typesense_key_here \
    TYPESENSE_COLLECTION=issues \
    EMBED_MODEL=all-MiniLM-L6-v2

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# http://localhost:8000/docs
# docker-compose build app
# https://github.com/kotyara12345678/recomendations

# docker exec -it a45c23f355b9_recommendation-app /bin/sh

# python -c "from main import app; print(app)"

# uvicorn main:app --host 0.0.0.0 --port 8000