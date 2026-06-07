FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml .
RUN uv sync
COPY . .
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin/:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "dispatcher.main:app", "--host", "0.0.0.0", "--port", "8000"]