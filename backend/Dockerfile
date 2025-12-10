FROM python:3.9-slim

WORKDIR /app

# Copy requirements from current directory (backend/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code to /app/backend so it can be verified as a module
COPY . /app/backend

# Set pythonpath to /app
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
