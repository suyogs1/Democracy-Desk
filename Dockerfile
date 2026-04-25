# Distroless or multi-stage slim
FROM python:3.11-slim as builder

WORKDIR /app

# Only copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final production image
FROM python:3.11-slim

WORKDIR /app

# Copy from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Ensure scripts in .local/bin are in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="."

EXPOSE 8080

# Use optimized gunicorn+uvicorn for efficiency
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--timeout-keep-alive", "0"]
