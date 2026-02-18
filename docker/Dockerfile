# Stage 1: Builder
FROM python:3.9-slim as builder

# Metadata
LABEL maintainer="devops-team@example.com" \
      description="Real-Time Cyber Threat Detection and Response System - Multi-stage Dockerfile"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy dependency files first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Remove unnecessary files (e.g., tests, docs) from the build stage
RUN rm -rf tests/ docs/

# Stage 2: Runtime
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Create non-root user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi7 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR $APP_HOME

# Copy application from builder stage
COPY --from=builder /app /app

# Set permissions for non-root user
RUN chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Entrypoint
ENTRYPOINT ["python", "main.py"]