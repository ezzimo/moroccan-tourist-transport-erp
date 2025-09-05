# backend/financial_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directories
RUN mkdir -p uploads/receipts uploads/reports

# Create non-root user once and own the app directory
RUN useradd --create-home --shell /bin/bash app \
 && chown -R app:app /app

# Ensure entrypoint has correct owner/permissions (overwrites the one from COPY . .)
COPY --chown=app:app --chmod=0755 entrypoint.sh /app/entrypoint.sh

# Drop privileges
USER app

# Expose port
EXPOSE 8006

# Start via entrypoint (which will run migrations + uvicorn)
ENTRYPOINT ["/app/entrypoint.sh"]
