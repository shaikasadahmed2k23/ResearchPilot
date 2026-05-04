FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create data directories
RUN mkdir -p data/chroma_db

# Expose port
EXPOSE 7860

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

