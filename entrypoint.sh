#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

MAX_RETRIES=60
RETRY_COUNT=0

while ! pg_isready -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-username}"; do
    RETRY_COUNT=$((RETRY_COUNT + 1))

    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "Error: PostgreSQL did not become ready in $MAX_RETRIES seconds. Exiting."
        exit 1
    fi

    sleep 1
done

echo "PostgreSQL is ready!"

python -c "import src.app; src.app.initialize_db()"

exec gunicorn -w 4 -b 0.0.0.0:8000 src.app:app