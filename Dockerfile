FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libpq-dev gcc supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

COPY supervisord.conf /etc/supervisord.conf

EXPOSE 8000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
