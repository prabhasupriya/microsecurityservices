# ============================
# Stage 1: Builder
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

# Install cron & tzdata
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# ⭐ FIX: Copy entire Python environment (not just lib)
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY --from=builder /app /app

# Ensure scripts executable
RUN chmod +x scripts/*

# Setup cron job
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

RUN mkdir -p /data /cron && chmod -R 755 /data /cron

EXPOSE 8080

CMD bash -c "cron -f & uvicorn api:app --host 0.0.0.0 --port 8080"
