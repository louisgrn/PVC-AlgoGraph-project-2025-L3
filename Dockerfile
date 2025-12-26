FROM python:3.9-slim

# Install system dependencies
# texlive-latex-base: Basic LaTeX support
# texlive-latex-extra: Additional LaTeX packages (often needed)
# curl: For sending webhooks
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-lang-french \
    texlive-pictures \
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
