# ==================================================
# 🚀 Dockerfile pour Chatbot CHSM
# ==================================================
# Chatbot de support IT pour l'hôpital CHSM
# Backend: FastAPI + Groq LLM
# Frontend: Streamlit
# Base de données vectorielle: ChromaDB
# ==================================================

FROM python:3.12-slim

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
RUN mkdir -p /app/backend /app/documents /app/chroma_db /app/logs

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code
COPY backend/ ./backend/
COPY interface-streamlit.py .
COPY .streamlit/ ./.streamlit/

# Exposer les ports
# 8000: FastAPI Backend
# 8501: Streamlit Frontend
EXPOSE 8000 8501

# Script de démarrage
# Lance FastAPI en arrière-plan et Streamlit en avant-plan
CMD uvicorn backend.app:app --host 0.0.0.0 --port 8000 & \
    streamlit run interface-streamlit.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
