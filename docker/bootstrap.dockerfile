# Bootstrap Container for Role and User Creation
# This container runs the bootstrap script during deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-bootstrap.txt .
RUN pip install --no-cache-dir -r requirements-bootstrap.txt

# Copy bootstrap script and related files
COPY scripts/bootstrap_roles_users.py scripts/
COPY scripts/README.md scripts/

# Make script executable
RUN chmod +x scripts/bootstrap_roles_users.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python3", "scripts/bootstrap_roles_users.py", "--environment", "production"]

