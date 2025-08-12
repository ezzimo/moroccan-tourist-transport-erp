#!/usr/bin/env bash
set -e  # Exit immediately on error

echo "[entrypoint] Starting authentication service..."

# Wait for the database to be ready
echo "[entrypoint] Waiting for database at $DATABASE_URL..."
python <<'PY'
import os, time, sys
from urllib.parse import urlparse
import psycopg2

url = os.environ.get("DATABASE_URL")
if not url:
    print("DATABASE_URL environment variable is not set", file=sys.stderr)
    sys.exit(1)

p = urlparse(url)
for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=p.path.lstrip('/'),
            user=p.username,
            password=p.password,
            host=p.hostname,
            port=p.port or 5432,
        )
        conn.close()
        print("[entrypoint] Database is ready!")
        break
    except Exception as e:
        print(f"[entrypoint] Database not ready ({e}), retrying {i+1}/30...")
        time.sleep(1)
else:
    print("[entrypoint] ERROR: Database not ready after 30s", file=sys.stderr)
    sys.exit(1)
PY

# Run Alembic migrations
echo "[entrypoint] Running Alembic migrations..."
alembic upgrade head

# Start Uvicorn
echo "[entrypoint] Starting Uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
