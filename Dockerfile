FROM python:3.13-slim

# Рабочая директория
WORKDIR /app

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (uv sync создает .venv автоматически)
RUN uv sync --locked --no-dev

# Копируем остальные файлы проекта
COPY . .

# Добавляем рабочую директорию в PYTHONPATH, чтобы Python мог найти модуль svc
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Открытие порта
EXPOSE 8080

# Запуск приложения через uv run (автоматически использует .venv)
CMD ["uv", "run", "gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080"]