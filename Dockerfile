FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies untuk easyocr (butuh beberapa system libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua source code ke dalam container
COPY . .

# Expose port FastAPI
EXPOSE 8000

# Jalankan aplikasi FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
