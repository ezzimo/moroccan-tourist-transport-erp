FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including runtime libs for ReportLab
RUN apt-get update && apt-get install -y \
    gcc \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify ReportLab installation at build time
RUN python -c "import reportlab; print('ReportLab version:', getattr(reportlab, 'Version', 'unknown'))"

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8002

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]