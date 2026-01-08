FROM python:3.11-slim

RUN apt-get update && apt-get install --no-install-recommends --yes build-essential python3-dev libffi-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --only=main --no-interaction --no-ansi

COPY notification_service/ .

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["faststream", "run", "infrastructures.broker.broker:app"]
