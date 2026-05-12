FROM python:3.11-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Assuming requirements are placed in the root or backend folder
# We will create a consolidated requirements file or use backend's
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Add a non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy application code (Backend, Agents, RAG)
COPY backend/ /app/backend/
COPY agents/ /app/agents/
COPY rag/ /app/rag/

# Set PYTHONPATH so absolute imports work
ENV PYTHONPATH=/app

# Create directories for persistent storage (Chroma, Uploads) and set permissions
RUN mkdir -p /app/var/uploads /app/var/chroma && chown -R appuser:appgroup /app/var

USER appuser

EXPOSE 8000

# The default command runs the FastAPI app
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
