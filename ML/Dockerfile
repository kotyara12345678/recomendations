FROM python:3.11-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY configs ./configs
COPY data ./data

RUN uv sync

CMD ["bash"]