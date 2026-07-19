# ══════════════════════════════════════════════════════════════════
# Dockerfile — FastAPI Python AI Microservice (ai-service/)
# Multi-stage: builder → lean production image
# ══════════════════════════════════════════════════════════════════

# ── Stage 1: Build / install dependencies ─────────────────────────
FROM python:3.11-slim AS builder

LABEL stage="builder"

WORKDIR /app

# Install build tools for compiled packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into an isolated prefix
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production image ─────────────────────────────────────
FROM python:3.11-slim AS production

LABEL app="cx-guardian-ai-service"
LABEL version="1.0.0"

# Security: run as non-root user
RUN groupadd -g 1001 aigroup && \
    useradd  -u 1001 -g aigroup -m -s /bin/sh aiuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=aiuser:aigroup . .

# Switch to non-root user
USER aiuser

# Expose FastAPI port
EXPOSE 8000

# Healthcheck — calls GET /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start Uvicorn with production settings
# --workers 1 keeps shared state consistent inside the container
# Scale horizontally with Docker Compose / Kubernetes replicas
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--http", "httptools", \
     "--log-level", "info", \
     "--access-log"]
