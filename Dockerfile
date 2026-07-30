# syntax=docker/dockerfile:1
# slim base: smaller attack surface and faster pull than the full python image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# requirements.txt is copied and installed before the app code so this layer
# stays cached across rebuilds unless a dependency actually changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY app.py ./

# non-root user: limits the blast radius if the app is ever compromised
RUN mkdir -p data/raw data/processed \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# lets Docker/Azure App Service detect a stuck container and restart it
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').status==200 else 1)"

# 0.0.0.0 binds all interfaces inside the container; localhost would be
# unreachable from outside it, even with the port published
ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
