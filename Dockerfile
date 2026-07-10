FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libgdk-pixbuf-xlib-2.0-0 \
    shared-mime-info \
    postgresql-client \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY requirements.txt .
COPY *.py ./
COPY backup_cron.sh entrypoint-cron.sh ./
COPY templates/ templates/
COPY static/ static/

ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN mkdir -p instance static/uploads backups && \
    chmod +x entrypoint-cron.sh backup_cron.sh 2>/dev/null || true

VOLUME ["/app/static/uploads", "/app/backups"]

EXPOSE 5002

CMD exec gunicorn --bind 0.0.0.0:5002 --workers ${GUNICORN_WORKERS:-2} --timeout 120 app:app
