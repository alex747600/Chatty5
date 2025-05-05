FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

# Устанавливаем netcat и убираем мусор
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip install "faststream[rabbit]"

# Делаем скрипт исполняемым
RUN chmod +x /app/docker-entrypoint.sh

# Открываем порт
EXPOSE 8007

# Запускаем сервис через entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

