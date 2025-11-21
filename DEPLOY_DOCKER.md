# 🐳 Guide de Déploiement Docker - IT Support Chatbot

## 📋 Table des Matières
1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Configuration Initiale](#configuration-initiale)
4. [Déploiement Local](#déploiement-local)
5. [Plateformes de Déploiement Gratuites](#plateformes-de-déploiement-gratuites)
6. [Dépannage](#dépannage)

---

## 🎯 Introduction

Ce guide vous aide à déployer le chatbot IT Support avec **Docker** sur différentes plateformes **gratuites**, sans modifier l'architecture actuelle.

### ✅ Avantages de Docker
- ✨ **Portabilité** : Fonctionne partout (Windows, Linux, Mac)
- 🔒 **Isolation** : Environnement reproductible
- 🚀 **Déploiement facile** : Une commande pour tout lancer
- 💰 **Gratuit** : Compatible avec plusieurs plateformes gratuites

---

## 🔧 Prérequis

### 1. Installer Docker Desktop

**Windows/Mac** :
- Télécharger : https://www.docker.com/products/docker-desktop
- Installer et redémarrer
- Vérifier l'installation :
```powershell
docker --version
docker-compose --version
```

### 2. Fichiers requis dans votre projet
```
chatbot-chsm/
├── Dockerfile              ✅ (créé)
├── docker-compose.yml      ✅ (créé)
├── .dockerignore           ✅ (créé)
├── .env                    ⚠️ (à configurer)
├── requirements.txt        ✅
├── interface-streamlit.py  ✅
├── backend/
│   ├── app.py             ✅
│   └── document_processor.py ✅
└── documents/             ✅ (vos fichiers PDF/Word)
```

---

## ⚙️ Configuration Initiale

### 1. Créer le fichier `.env`

Copier `.env.example` vers `.env` :
```powershell
Copy-Item .env.example .env
```

Éditer `.env` avec vos clés API :
```env
# Groq API (OBLIGATOIRE)
GROQ_API_KEY=gsk_votre_cle_api_ici
GROQ_MODEL=llama-3.3-70b-versatile

# Configuration
DOCUMENTS_DIR=./documents
ENVIRONMENT=production
```

> 🔑 **Obtenir une clé Groq** : https://console.groq.com/keys (gratuit)

### 2. Vérifier les documents

Assurez-vous que vos documents sont dans le dossier `documents/` :
```powershell
ls documents/
```

---

## 🚀 Déploiement Local

### Méthode 1 : Docker Compose (Recommandée)

**Lancer l'application complète** :
```powershell
docker-compose up --build
```

**Accéder à l'application** :
- 🌐 Frontend Streamlit : http://localhost:8501
- 🔌 Backend API : http://localhost:8000
- 📊 Health Check : http://localhost:8000/api/health

**Arrêter l'application** :
```powershell
# Ctrl+C puis
docker-compose down
```

### Méthode 2 : Docker seul

**Construire l'image** :
```powershell
docker build -t chatbot-it-support .
```

**Lancer le conteneur** :
```powershell
docker run -d `
  --name chatbot `
  -p 8000:8000 `
  -p 8501:8501 `
  -e GROQ_API_KEY=votre_cle `
  -v ${PWD}/documents:/app/documents `
  -v ${PWD}/chroma_db:/app/chroma_db `
  chatbot-it-support
```

**Voir les logs** :
```powershell
docker logs -f chatbot
```

**Arrêter et supprimer** :
```powershell
docker stop chatbot
docker rm chatbot
```

---

## 💰 Plateformes de Déploiement Gratuites

### 🥇 Option 1 : Render.com (RECOMMANDÉ)

**Avantages** :
- ✅ **750h/mois gratuites** (suffisant pour 24/7)
- ✅ SSL automatique
- ✅ Déploiement depuis GitHub
- ✅ Variables d'environnement sécurisées

**Étapes** :

1. **Créer un compte** : https://render.com/

2. **Connecter votre dépôt GitHub** :
   - Pusher votre code sur GitHub
   - Cliquer "New +" → "Web Service"
   - Connecter le repo `StageTI`

3. **Configuration du service** :
   - **Name** : `chatbot-it-support`
   - **Region** : `Frankfurt` (plus proche)
   - **Branch** : `main`
   - **Root Directory** : (vide)
   - **Environment** : `Docker`
   - **Instance Type** : `Free`

4. **Variables d'environnement** :
   ```
   GROQ_API_KEY = votre_cle_groq
   GROQ_MODEL = llama-3.3-70b-versatile
   ENVIRONMENT = production
   ```

5. **Déployer** :
   - Cliquer "Create Web Service"
   - Attendre ~5-10 minutes
   - URL publique : `https://chatbot-it-support.onrender.com`

**Limitations gratuites** :
- ⚠️ Mise en veille après 15 min d'inactivité (redémarre en ~30s)
- ⚠️ 512 MB RAM (suffisant pour ce projet)

---

### 🥈 Option 2 : Railway.app

**Avantages** :
- ✅ **$5 crédit/mois gratuit** (~500h)
- ✅ Déploiement ultra-simple
- ✅ Pas de mise en veille

**Étapes** :

1. **Compte** : https://railway.app/ (connexion GitHub)

2. **Nouveau projet** :
   - "New Project" → "Deploy from GitHub repo"
   - Sélectionner `StageTI`

3. **Configuration** :
   - Railway détecte automatiquement le `Dockerfile`
   - Ajouter variables :
     ```
     GROQ_API_KEY
     GROQ_MODEL
     ENVIRONMENT=production
     ```

4. **Port** :
   - Railway expose automatiquement le port 8501
   - Générer un domaine : Settings → Generate Domain

**URL publique** : `https://chatbot-it-support-production.up.railway.app`

---

### 🥉 Option 3 : Fly.io

**Avantages** :
- ✅ Gratuit jusqu'à 3 petites VMs
- ✅ Déploiement global rapide

**Étapes** :

1. **Installer CLI** :
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

2. **Login** :
```powershell
fly auth login
```

3. **Créer l'app** :
```powershell
fly launch
# Suivre les instructions
# Nom: chatbot-it-support
# Region: fra (Frankfurt)
# PostgreSQL: No
# Redis: No
```

4. **Configurer secrets** :
```powershell
fly secrets set GROQ_API_KEY=votre_cle
fly secrets set GROQ_MODEL=llama-3.3-70b-versatile
```

5. **Déployer** :
```powershell
fly deploy
```

6. **URL publique** :
```powershell
fly open
```

---

### 🆓 Option 4 : Hugging Face Spaces

**Avantages** :
- ✅ Totalement gratuit
- ✅ Spécialisé pour apps ML/AI

**Configuration** :

1. Créer un Space : https://huggingface.co/spaces
2. Choisir "Docker"
3. Uploader :
   - `Dockerfile`
   - Tout le code
   - Ajouter secret `GROQ_API_KEY` dans Settings

---

## 🔍 Comparaison des Plateformes

| Plateforme       | Prix      | RAM  | Veille | SSL | Recommandation |
|------------------|-----------|------|--------|-----|----------------|
| **Render.com**   | Gratuit   | 512M | ✅ Oui | ✅  | ⭐⭐⭐⭐⭐       |
| **Railway.app**  | $5/mois   | 512M | ❌ Non | ✅  | ⭐⭐⭐⭐         |
| **Fly.io**       | Gratuit   | 256M | ❌ Non | ✅  | ⭐⭐⭐          |
| **HF Spaces**    | Gratuit   | 16G  | ❌ Non | ✅  | ⭐⭐⭐          |

**Meilleur choix** : **Render.com** pour démarrer (facile + gratuit)

---

## 🛠️ Dépannage

### ❌ Problème : "Cannot connect to Docker daemon"

**Solution (Windows)** :
1. Ouvrir Docker Desktop
2. Attendre qu'il démarre complètement
3. Réessayer la commande

---

### ❌ Problème : "GROQ_API_KEY not found"

**Solution** :
```powershell
# Vérifier le fichier .env
cat .env

# Reconstruire avec la variable
docker-compose up --build
```

---

### ❌ Problème : "Port already in use"

**Solution** :
```powershell
# Trouver le processus utilisant le port
netstat -ano | findstr :8501

# Tuer le processus (remplacer PID)
taskkill /PID 12345 /F

# Ou changer le port dans docker-compose.yml
ports:
  - "8502:8501"
```

---

### ❌ Problème : Image trop volumineuse

**Solution** :
```powershell
# Nettoyer les anciennes images
docker system prune -a

# Vérifier la taille
docker images
```

---

### 🔍 Commandes de debug utiles

```powershell
# Voir les conteneurs actifs
docker ps

# Logs en temps réel
docker logs -f chatbot

# Entrer dans le conteneur
docker exec -it chatbot /bin/bash

# Inspecter le réseau
docker network inspect chatbot-network

# Voir l'utilisation des ressources
docker stats
```

---

## 📊 Vérification du Déploiement

### ✅ Checklist de test

1. **Health Check** :
   ```powershell
   curl http://localhost:8000/api/health
   # Doit retourner: {"status":"healthy"}
   ```

2. **Indexation des documents** :
   ```powershell
   curl http://localhost:8000/
   # Vérifier: "documents_indexed" > 0
   ```

3. **Test de question** :
   ```powershell
   curl -X POST http://localhost:8000/api/chat `
     -H "Content-Type: application/json" `
     -d '{"question":"Comment réinitialiser mon mot de passe?"}'
   ```

4. **Interface Streamlit** :
   - Ouvrir http://localhost:8501
   - Poser une question
   - Vérifier que la réponse utilise les sources

---

## 🎯 Mise en Production

### Recommandations de sécurité

1. **Variables d'environnement** :
   - ❌ Ne JAMAIS commiter `.env`
   - ✅ Utiliser les secrets de la plateforme

2. **Monitoring** :
   - Activer les alertes (Render, Railway)
   - Vérifier les logs régulièrement

3. **Sauvegardes** :
   ```powershell
   # Backup de la base ChromaDB
   docker cp chatbot:/app/chroma_db ./backup_chroma_db
   ```

4. **Mises à jour** :
   ```powershell
   # Reconstruire avec les dernières dépendances
   docker-compose build --no-cache
   docker-compose up -d
   ```

---

## 📞 Support

**Problèmes** : Ouvrir une issue sur GitHub
**Documentation** : Consulter `README.md` et `API_DOCUMENTATION.md`

---

## 🎉 Prochaines Étapes

1. ✅ Déployer localement avec Docker
2. ✅ Tester toutes les fonctionnalités
3. ✅ Choisir une plateforme (Render recommandé)
4. ✅ Configurer le déploiement
5. ✅ Partager l'URL publique avec les utilisateurs

**Bon déploiement ! 🚀**
