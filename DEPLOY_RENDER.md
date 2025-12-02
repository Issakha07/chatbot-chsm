# Guide de Déploiement sur Render.com
# Hébergement du Backend (Gratuit pour commencer)

## 🚀 Étape 1: Préparer le Repository

### 1.1 Créer un fichier render.yaml

Créez ce fichier à la racine du projet:

```yaml
services:
  - type: web
    name: chatbot-backend
    env: python
    region: frankfurt  # ou oregon, singapore
    plan: free  # Gratuit pour commencer
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false  # À configurer manuellement
      - key: GROQ_MODEL
        value: llama-3.3-70b-versatile
      - key: DOCUMENTS_DIR
        value: ./documents
      - key: PYTHON_VERSION
        value: 3.12.0
```

### 1.2 Mettre à jour requirements.txt

Ajoutez:
```
gunicorn==21.2.0
uvicorn[standard]==0.24.0
```

### 1.3 Créer un Procfile (optionnel)

```
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

---

## 🌐 Étape 2: Déployer sur Render.com

### 2.1 Créer un compte

1. Allez sur https://render.com
2. Cliquez "Get Started" ou "Sign Up"
3. Connectez-vous avec GitHub

### 2.2 Créer un nouveau Web Service

1. Dashboard → "New +" → "Web Service"
2. Connectez votre repository GitHub `chatbot-chsm`
3. Configuration:
   - **Name:** `chatbot-backend` (ou votre choix)
   - **Region:** Frankfurt (Europe) ou Oregon (USA)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (0€/mois, 750h/mois)

### 2.3 Configurer les Variables d'Environnement

Dans l'onglet "Environment":

```
GROQ_API_KEY = gsk_votre_cle_ici
GROQ_MODEL = llama-3.3-70b-versatile
DOCUMENTS_DIR = ./documents
PYTHON_VERSION = 3.12.0
```

### 2.4 Déployer

Cliquez "Create Web Service"

Le déploiement prend 3-5 minutes.

---

## 🔗 Étape 3: Configurer l'URL

Une fois déployé, Render vous donne une URL:

```
https://chatbot-backend-XXXXX.onrender.com
```

### Tester l'API

```bash
curl https://chatbot-backend-XXXXX.onrender.com/health

# Devrait retourner:
{"status": "healthy", "timestamp": "..."}
```

---

## 🔐 Étape 4: Configurer les Clients

### 4.1 Générer une API Key pour un client

```python
# Script pour générer des clés
import secrets

def generate_api_key(plan: str = "business"):
    random_part = secrets.token_urlsafe(32)
    return f"sk_{plan}_{random_part}"

# Exemple
client_key = generate_api_key("business")
print(f"Clé pour le client: {client_key}")
```

### 4.2 Ajouter la clé dans backend/app.py

```python
VALID_API_KEYS = {
    "client_hopital_A": "sk_business_abc123...",
    "client_hopital_B": "sk_starter_xyz789...",
    # Nouvelle clé
    "client_hopital_C": "sk_business_NOUVELLE_CLE_GENEREE",
}
```

### 4.3 Redéployer

Git commit + push → Render redéploie automatiquement

---

## 📦 Étape 5: Livrer au Client

### 5.1 Package à envoyer

Créez un ZIP avec:

```
client-hopital-A.zip
├── interface-streamlit.py
├── style.css
├── .env.example
├── requirements.txt
├── README.md
├── LICENSE.txt
└── API_KEY.txt  ← Contient la clé unique du client
```

### 5.2 Fichier API_KEY.txt

```
==============================================
VOTRE CLÉ API - CHATBOT IT SUPPORT
==============================================

Clé API: sk_business_VOTRE_CLE_ICI

URL de l'API: https://chatbot-backend-XXXXX.onrender.com/api/chat

Plan: Business
Quota: 10 000 requêtes/mois
Rate limit: 30 requêtes/minute

==============================================
⚠️ IMPORTANT - NE PARTAGEZ PAS CETTE CLÉ
==============================================

Cette clé est unique et personnelle.
En cas de fuite, contactez immédiatement:
support@votre-entreprise.com

Date d'émission: 2025-12-02
Valide jusqu'à: 2026-12-02 (renouvellement automatique)
```

### 5.3 Configuration client (.env)

Le client crée un fichier `.env`:

```env
BACKEND_API_URL=https://chatbot-backend-XXXXX.onrender.com/api/chat
API_KEY=sk_business_VOTRE_CLE_ICI
```

---

## 💰 Étape 6: Gestion des Abonnements

### 6.1 Plans Render.com

**Free:**
- 750 heures/mois
- 512 MB RAM
- Serveur se met en veille après 15 min d'inactivité
- Bon pour DEMO

**Starter ($7/mois):**
- Toujours actif (pas de veille)
- 512 MB RAM
- SSL automatique
- Bon pour 5-10 clients

**Standard ($25/mois):**
- 2 GB RAM
- Auto-scaling
- Metrics avancées
- Bon pour 20-50 clients

**Pro ($85/mois):**
- 4 GB RAM
- Load balancing
- Support prioritaire
- Bon pour 100+ clients

### 6.2 Tarification Client

Vos prix clients (exemple):

```
Plan Starter: 99€/mois
→ Votre marge: 92€/mois (si Starter Render)

Plan Business: 299€/mois
→ Votre marge: 274€/mois (si Standard Render)

Plan Enterprise: 999€/mois
→ Votre marge: 914€/mois (si Pro Render)
```

---

## 📊 Étape 7: Monitoring

### 7.1 Dashboard Render

- Métriques CPU/RAM
- Logs en temps réel
- Alertes automatiques

### 7.2 Endpoint de Métriques

```python
# Déjà dans backend/app.py
@app.get("/api/metrics")
async def get_metrics():
    return {
        "total_requests": metrics['total_requests'],
        "success_rate": metrics['successful_requests'] / max(metrics['total_requests'], 1),
        "avg_response_time": metrics['total_response_time'] / max(metrics['successful_requests'], 1)
    }
```

### 7.3 Alertes par Email

Render peut envoyer des alertes si:
- Service down
- CPU > 90%
- RAM > 90%
- Erreurs répétées

---

## 🔄 Étape 8: Mises à Jour

### 8.1 Workflow de Mise à Jour

```bash
# 1. Développement local
git checkout -b feature/nouvelle-fonctionnalite

# 2. Tests
pytest backend/test_app.py

# 3. Merge vers main
git checkout main
git merge feature/nouvelle-fonctionnalite

# 4. Push → Déploiement automatique
git push origin main
```

Render détecte le push et redéploie automatiquement (2-3 minutes)

### 8.2 Rollback en cas de problème

Dans Render Dashboard:
- Onglet "Events"
- Sélectionner un déploiement précédent
- Cliquer "Redeploy"

---

## 🔐 Étape 9: Sécurité Avancée

### 9.1 HTTPS Automatique

Render fournit SSL gratuit (Let's Encrypt)

### 9.2 Rate Limiting Global

Ajouter dans backend/app.py:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat")
@limiter.limit("100/minute")  # 100 requêtes/min par IP
async def chat(...):
    ...
```

### 9.3 Protection DDoS

Render inclut protection DDoS basique.
Pour plus: Cloudflare en front.

---

## 💡 Conseils Pro

### 9.1 Domaine Personnalisé

Au lieu de `chatbot-backend-XXXXX.onrender.com`:

1. Achetez un domaine: `api.votre-entreprise.com`
2. Render → Settings → Custom Domain
3. Ajoutez le CNAME DNS
4. SSL automatique

### 9.2 Base de Données Séparée

Pour stocker les API Keys:

```yaml
# render.yaml
databases:
  - name: chatbot-db
    databaseName: chatbot
    user: chatbot
```

### 9.3 Backup Automatique

Les documents et chroma_db peuvent être backupés vers:
- Google Drive (via DVC)
- AWS S3
- Render Persistent Disk

---

## 📞 Support Render

- Documentation: https://render.com/docs
- Support: support@render.com
- Status: https://status.render.com

---

## ✅ Checklist Finale

Avant de lancer en production:

- [ ] Backend déployé sur Render
- [ ] Variables d'environnement configurées
- [ ] SSL actif (HTTPS)
- [ ] API Keys générées pour chaque client
- [ ] Quotas configurés
- [ ] Logs et monitoring actifs
- [ ] Package client créé et testé
- [ ] Documentation client envoyée
- [ ] Contrat et facture préparés
- [ ] Support client configuré

---

**Prêt à lancer ! 🚀**

Votre premier client peut maintenant se connecter avec sa clé API unique et vous générez des revenus récurrents mensuels sans que le client n'ait accès à votre code backend.
