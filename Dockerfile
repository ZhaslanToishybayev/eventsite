# Dockerfile (обновлённый)
FROM python:3.11-slim

# Install system dependencies (gcc, libpq-dev, postgresql-client, libmagic)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev postgresql-client libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /proj
# Копируем проект
COPY . /proj

# Переименовываем gunicorn.conf.py чтобы он не загружался автоматически
RUN mv /proj/gunicorn.conf.py /proj/gunicorn.conf.py.bak || true

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
