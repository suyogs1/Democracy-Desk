# Distroless-inspired multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final production image
FROM python:3.11-slim

WORKDIR /app

# Copy from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Environment setup
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="."

EXPOSE 8080

# Use Gunicorn with Uvicorn workers for high-efficiency production serving
# This ensures optimal CPU utilization and request handling
CMD ["gunicorn", "api.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--timeout", "0"]
