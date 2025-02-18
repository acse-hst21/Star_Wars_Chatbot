FROM python:3.10-slim

# Ensure PostgreSQL client utilities are installed
# Then remove extra files to reduce size of image
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ /app/src
COPY entrypoint.sh /app/entrypoint.sh

# Ensure script has appropriate permissions
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]