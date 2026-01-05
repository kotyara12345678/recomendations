FROM python:3.11-slim

# Системные зависимости (минимум)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv (быстро)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

WORKDIR /app

COPY requirements.txt .

RUN uv pip install --system --no-cache -r requirements.txt

COPY trainer/ ./trainer
COPY embedder/ ./embedder
COPY data/ ./data

WORKDIR /app/trainer

CMD ["python", "trainer.py"]