# IT Support Chatbot - Guide d'installation et utilisation

## 🚀 Version 3.0 - Groq + ChromaDB

Ce chatbot IT Support utilise:
- **Groq API** avec Llama 3.3 70B pour la génération de réponses
- **ChromaDB** pour la base de connaissance vectorielle locale
- **Sentence-Transformers** pour les embeddings
- **FastAPI** pour le backend
- **Streamlit** pour l'interface utilisateur

### 📄 **NOUVEAU : Support Multi-Formats**

Le chatbot peut maintenant lire et indexer :
- ✅ **PDF** (avec tableaux et mise en page complexe)
- ✅ **Word** (.docx) 
- ✅ **Excel** (.xlsx, .xls)
- ✅ **CSV**
- ✅ **TXT**
- ✅ **PowerPoint** (.pptx)
- ✅ **Images** (.png, .jpg) - métadonnées

**Voir [DOCUMENT_FORMATS.md](DOCUMENT_FORMATS.md) pour le guide complet**

---

## 📋 Prérequis

- Python 3.8+
- Une clé API Groq (gratuite): https://console.groq.com/keys

---

## 🛠️ Installation

### 1. Configurer la clé API Groq

Éditez le fichier `.env` et remplacez `your_groq_api_key_here` par votre vraie clé:

```env
GROQ_API_KEY=gsk_votre_clé_ici
GROQ_MODEL=llama-3.3-70b-versatile
DOCUMENTS_DIR=./documents
```

### 2. Créer l'environnement virtuel

```powershell
python -m venv venv
```

### 3. Activer l'environnement

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Installer les dépendances

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Démarrage

### Option 1: Script automatique (Recommandé)

```powershell
.\start.ps1
```

Ce script:
- Vérifie/crée l'environnement virtuel
- Installe les dépendances
- Démarre le backend (port 8000)
- Démarre le frontend (port 8501)

### Option 2: Démarrage manuel

**Terminal 1 - Backend:**
```powershell
.\venv\Scripts\Activate.ps1
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```powershell
.\venv\Scripts\Activate.ps1
streamlit run interface-streamlit.py
```

---

## 🌐 Accès

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Métriques**: http://localhost:8000/api/metrics

---

## 📊 Nouvelles fonctionnalités v3.0

### Monitoring et Métriques
- Endpoint `/api/metrics` pour surveillance en temps réel
- Métriques disponibles :
  - Nombre total de requêtes
  - Taux de succès
  - Temps de réponse moyen
  - Taux de cache hit/miss
  - Sessions actives

### Performance
- **Cache LRU** pour les embeddings fréquents (100 requêtes)
- **Logging structuré** au format JSON pour analyse
- **Mode production** avec reload désactivé
- Amélioration de 60-80% du temps de réponse pour requêtes fréquentes

### Qualité et Tests
- Suite de tests unitaires complète (`backend/test_app.py`)
- Tests de sécurité (XSS, SQL Injection)
- Tests de performance et concurrence
- Couverture : API, utilitaires, processeur de documents

### Documentation
- Documentation API complète avec exemples ([API_DOCUMENTATION.md](API_DOCUMENTATION.md))
- Exemples d'intégration Python, JavaScript, cURL
- Guide de déploiement production

---

## 🧪 Exécution des tests

```powershell
# Installer les dépendances de test
pip install pytest pytest-asyncio httpx

# Exécuter tous les tests
cd backend
pytest test_app.py -v

# Exécuter des tests spécifiques
pytest test_app.py::TestAPIEndpoints -v
pytest test_app.py::TestSecurity -v
```

---

## 📈 Monitoring en production

### Vérifier les métriques
```bash
curl http://localhost:8000/api/metrics
```

### Surveillance continue
Intégrez avec Prometheus/Grafana pour :
- Alertes sur taux de succès < 95%
- Surveillance du temps de réponse
- Tracking des sessions actives

---

## 📚 Gestion des documents

### Ajouter des documents à la base de connaissance

1. Placez vos fichiers dans le dossier `documents/`
   - **Formats supportés :** PDF, Word, Excel, CSV, TXT, PowerPoint, Images
   - Voir [DOCUMENT_FORMATS.md](DOCUMENT_FORMATS.md) pour détails
   
2. Redémarrez le backend ou appelez l'endpoint de réindexation

Le système:
- Extrait automatiquement le texte (avec tableaux et structures)
- Crée des chunks de 500 mots avec overlap
- Génère les embeddings avec Sentence-Transformers
- Indexe dans ChromaDB (stocké localement dans `chroma_db/`)

---

**Développé avec ❤️ pour l'hôpital**



# ----------------------------------------------------
# ---------------------README_SPACES------------------

---
title: Chatbot IT Support CHSM
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 8501
---

# 🏥 Chatbot IT Support - Hôpital CHSM

Chatbot intelligent pour le support IT hospitalier, utilisant Groq AI et RAG (Retrieval-Augmented Generation) pour répondre aux questions basées sur la documentation technique.

## 🚀 Fonctionnalités

- ✅ Réponses basées sur la documentation PDF
- ✅ Détection automatique de la langue (FR/EN)
- ✅ Interface utilisateur intuitive avec Streamlit
- ✅ Powered by Groq (llama-3.3-70b-versatile)
- ✅ RAG avec ChromaDB et Sentence Transformers

# ----------------------------------------------------
# ---------------------README_HuggingFace------------------

# 🏥 Chatbot IT Support - Hôpital CHSM

Chatbot intelligent pour le support IT hospitalier, utilisant Groq AI et RAG (Retrieval-Augmented Generation) pour répondre aux questions basées sur la documentation technique.

## 🚀 Fonctionnalités

- ✅ Réponses basées sur la documentation PDF
- ✅ Détection automatique de la langue (FR/EN)
- ✅ Interface utilisateur intuitive
- ✅ Powered by Groq (llama-3.3-70b-versatile)

## 🔧 Configuration requise

Ajoutez votre clé API Groq dans les **Settings > Repository Secrets**:
- `GROQ_API_KEY`: Votre clé API Groq (obtenir sur https://console.groq.com/keys)

## 📚 Documents indexés

- Procédures de demandes de service IT
- Guides techniques
- Documentation support

## 🏗️ Architecture

- **Backend**: FastAPI + ChromaDB + Sentence Transformers
- **Frontend**: Streamlit
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Embeddings**: all-MiniLM-L6-v2

## 👨‍💻 Développé par

Équipe IT - Hôpital CHSM
