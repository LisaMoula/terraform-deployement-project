# syntax=docker/dockerfile:1

# ---- Base image : Python slim (léger, officiel) ----
FROM python:3.11-slim AS base

# Bonnes pratiques Python en conteneur.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ---- Dépendances (couche mise en cache tant que requirements.txt ne change pas) ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Code applicatif ----
COPY src/ ./src/
COPY app.py ./

# Zones de données (Landing/Gold) créées et accessibles en écriture.
RUN mkdir -p data/raw data/processed

# ---- Sécurité : exécution en utilisateur non-root ----
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Streamlit écoute sur 8501.
EXPOSE 8501

# Healthcheck sur l'endpoint interne de Streamlit.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').status==200 else 1)"

ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
