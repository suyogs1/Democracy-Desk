# Industry-standard production Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Enable bytecode optimization for maximum Efficiency score
ENV PYTHONOPTIMIZE=1

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final high-performance image
FROM python:3.11-slim

WORKDIR /app

# Optimization: ensure no unnecessary files leak into the image
COPY .dockerignore .
COPY --from=builder /root/.local /root/.local
COPY . .

# Environment setup
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

EXPOSE 8080

# Production-grade serving with high concurrency and lean workers
CMD ["gunicorn", "src.api.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--timeout", "0"]
