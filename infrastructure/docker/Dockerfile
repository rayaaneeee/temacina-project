# ---- infrastructure/docker/Dockerfile ----
# Multi‑stage Dockerfile for the Django API service

# ---------- Builder stage ----------
FROM python:3.11-slim AS builder

# Install build‑time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Create a non‑root user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install Python build dependencies (using pip)
ENV PIP_NO_CACHE_DIR=1
COPY --chown=appuser pyproject.toml poetry.lock ./
RUN python -m pip install --upgrade pip setuptools && \
    pip install -r requirements/production.txt

# Copy the application source
COPY --chown=appuser . .

# ---------- Runtime stage ----------
FROM python:3.11-slim AS runtime

# Copy runtime packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /home/appuser /home/appuser

# Add entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Use non‑root user
USER appuser
WORKDIR /home/appuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
