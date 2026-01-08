FROM python:3.11-slim

RUN apt-get update && apt-get install --no-install-recommends --yes build-essential python3-dev libffi-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && poetry install --only=main --no-interaction --no-ansi

COPY siws_login_service/ .


EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

