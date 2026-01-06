FROM python:3.11-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY configs ./configs
COPY data ./data

ENV PYTHONPATH="/app/src:${PYTHONPATH}"

RUN uv sync

CMD ["bash"]