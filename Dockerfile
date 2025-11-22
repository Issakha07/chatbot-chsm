# ==================================================
# 🚀 Dockerfile pour Hugging Face Spaces
# ==================================================
# Ce fichier est optimisé pour le déploiement sur Hugging Face Spaces.
# Pour le développement local avec Docker Compose, utilisez Dockerfile.local
# ==================================================

FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Installer dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer répertoires
WORKDIR /app
RUN mkdir -p /app/backend /app/documents /app/chroma_db

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code
COPY backend/ ./backend/
COPY interface-streamlit.py .
COPY documents/ ./documents/

# Exposer le port Streamlit
EXPOSE 8501

# Script de démarrage combiné
CMD uvicorn backend.app:app --host 0.0.0.0 --port 8000 & \
    streamlit run interface-streamlit.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
