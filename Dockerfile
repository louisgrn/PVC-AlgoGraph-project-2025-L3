FROM python:3.9-slim

# Install system dependencies
# curl: For sending webhooks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose Flask port
EXPOSE 5000

# Run the entrypoint script
CMD ["./entrypoint.sh"]
