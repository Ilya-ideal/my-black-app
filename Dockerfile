FROM python:3.9-slim

# Security: use non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ .

# Security: change ownership and use non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Security: environment variables
ENV APP_VERSION=2.0.0
ENV DEPLOY_TIME=unknown
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]