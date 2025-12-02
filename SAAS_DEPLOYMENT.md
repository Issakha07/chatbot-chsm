# 🚀 Déploiement SaaS - Protéger votre Code

## Architecture Recommandée

```
┌───────────────────────────────────────────────────────────┐
│                    VOTRE SERVEUR (Caché)                  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Backend FastAPI + ChromaDB + DVC + Evidently        │ │
│  │ - Code source protégé                                │ │
│  │ - Base de données vectorielle                        │ │
│  │ - Authentification par API Key                       │ │
│  └─────────────────────────────────────────────────────┘ │
│                           ▲                               │
└───────────────────────────┼───────────────────────────────┘
                            │
                    HTTPS + API Key
                            │
┌───────────────────────────▼───────────────────────────────┐
│              CLIENT (Ce qu'ils reçoivent)                 │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Interface Streamlit UNIQUEMENT                       │ │
│  │ - Code frontend simple                               │ │
│  │ - Fichier .env avec URL de votre API                │ │
│  │ - Pas de backend, pas de ChromaDB, pas de secrets   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## 🔐 Étape 1 : Sécuriser le Backend

### 1.1 Ajouter l'authentification par API Key

**Modifier `backend/app.py` :**

```python
from fastapi import FastAPI, HTTPException, Header, Depends
import secrets

# Liste des API Keys valides (à stocker en BD en production)
VALID_API_KEYS = {
    "client_hopital_A": "sk_live_abc123...",
    "client_hopital_B": "sk_live_xyz789...",
}

def verify_api_key(x_api_key: str = Header(...)):
    """Vérifier la clé API"""
    if x_api_key not in VALID_API_KEYS.values():
        raise HTTPException(status_code=403, detail="API Key invalide")
    return x_api_key

@app.post("/api/chat", dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    # Votre code actuel...
```

### 1.2 Déployer le Backend sur un Serveur

**Options de déploiement :**

#### Option A : Render.com (Facile, Gratuit pour commencer)
```bash
# 1. Créer un compte sur render.com
# 2. Connecter votre repo GitHub
# 3. Créer un "Web Service"
# 4. Variables d'environnement :
GROQ_API_KEY=votre_clé
ALLOWED_ORIGINS=https://client-hopital.streamlit.app
```

#### Option B : AWS EC2 (Professionnel)
```bash
# Instance EC2 + Docker
docker-compose up -d
# Configure le firewall pour autoriser seulement HTTPS
```

#### Option C : Railway.app (Simple)
```bash
# Déploiement automatique depuis GitHub
# URL générée : https://votre-chatbot.up.railway.app
```

---

## 📦 Étape 2 : Créer la Version Client

### 2.1 Créer un dossier `client-package/`

```
client-package/
├── interface-streamlit.py   ← Frontend uniquement
├── style.css                ← Styles
├── .env.example             ← Template de configuration
├── requirements-client.txt  ← Dépendances minimales
└── README-CLIENT.md         ← Instructions pour le client
```

### 2.2 Version simplifiée de `interface-streamlit.py`

**Modifications :**
```python
# Configuration API (le client modifie juste .env)
API_URL = os.getenv("BACKEND_API_URL", "https://votre-serveur.com/api/chat")
API_KEY = os.getenv("API_KEY")  # Clé fournie par vous

# Ajouter l'API Key dans les requêtes
def send_message(question: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY  # ✅ Authentification
    }
    
    response = requests.post(
        API_URL,
        json={"question": question},
        headers=headers,
        timeout=30
    )
    return response.json()
```

### 2.3 Fichier `.env.example` pour le client

```env
# Configuration du client
BACKEND_API_URL=https://votre-chatbot-api.render.com/api/chat
API_KEY=sk_client_XXXXXXXXXX  # Fourni par vous lors de l'achat
```

### 2.4 `requirements-client.txt` (minimaliste)

```
streamlit==1.28.2
requests==2.31.0
python-dotenv==1.0.0
```

**PAS de :**
- ❌ fastapi
- ❌ chromadb
- ❌ sentence-transformers
- ❌ groq
- ❌ dvc
- ❌ evidently

---

## 💰 Étape 3 : Modèle Commercial

### Tarification Suggérée

```
┌─────────────────────────────────────────────────┐
│ Plan Starter                                    │
│ - 1 000 requêtes/mois                           │
│ - 1 API Key                                     │
│ - Support email                                 │
│ Prix : 99€/mois                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Plan Business                                   │
│ - 10 000 requêtes/mois                          │
│ - 3 API Keys                                    │
│ - Support prioritaire                           │
│ - Rapports mensuels                             │
│ Prix : 299€/mois                                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Plan Enterprise                                 │
│ - Requêtes illimitées                           │
│ - API Keys illimitées                           │
│ - Support 24/7                                  │
│ - Installation on-premise possible              │
│ Prix : Sur devis (1500€+/mois)                  │
└─────────────────────────────────────────────────┘
```

### Système de Quotas

**Ajouter dans `backend/app.py` :**

```python
from collections import defaultdict
from datetime import datetime

# Compteur de requêtes par API Key
usage_tracker = defaultdict(lambda: {"count": 0, "month": datetime.now().month})

QUOTA_LIMITS = {
    "sk_starter_": 1000,
    "sk_business_": 10000,
    "sk_enterprise_": 999999999,
}

def check_quota(api_key: str):
    """Vérifier si le quota n'est pas dépassé"""
    # Réinitialiser le compteur chaque mois
    current_month = datetime.now().month
    if usage_tracker[api_key]["month"] != current_month:
        usage_tracker[api_key] = {"count": 0, "month": current_month}
    
    # Trouver le quota
    prefix = api_key[:12]  # ex: sk_starter_
    limit = QUOTA_LIMITS.get(prefix, 1000)
    
    if usage_tracker[api_key]["count"] >= limit:
        raise HTTPException(
            status_code=429, 
            detail=f"Quota dépassé. Limite: {limit}/mois. Contactez-nous pour upgrader."
        )
    
    usage_tracker[api_key]["count"] += 1

@app.post("/api/chat")
async def chat(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    check_quota(api_key)  # ✅ Vérifier avant traitement
    # Traitement normal...
```

---

## 📜 Étape 4 : Licence et Contrat

### Fichier `LICENSE-CLIENT.txt`

```
LICENCE D'UTILISATION - CHATBOT IT SUPPORT

Copyright (c) 2025 [Votre Nom/Entreprise]

Cette licence vous autorise à :
✅ Utiliser l'interface frontend fournie
✅ Connecter l'interface à notre API backend
✅ Personnaliser l'apparence (couleurs, logos)

Vous N'ÊTES PAS autorisé à :
❌ Copier, modifier ou distribuer le code backend
❌ Partager votre API Key avec des tiers
❌ Reverse-engineer ou décompiler l'API
❌ Revendre le service sans accord écrit

En cas de violation, votre accès sera révoqué immédiatement
et des poursuites légales pourront être engagées.
```

---

## 🎯 Étape 5 : Livraison au Client

### Ce que vous leur donnez :

```
client-package-hopital-X.zip
├── interface-streamlit.py       ← Code frontend (visible OK)
├── style.css
├── .env.example
├── requirements-client.txt
├── LICENSE-CLIENT.txt
├── README-CLIENT.md            ← Instructions d'installation
└── API-KEY.txt                 ← Leur clé unique (sk_...)
```

### `README-CLIENT.md`

```markdown
# Installation - Chatbot IT Support

## Étape 1 : Configuration

1. Renommez `.env.example` en `.env`
2. Ouvrez `.env` et collez votre API Key :
   ```
   API_KEY=sk_business_VOTRE_CLE_FOURNIE
   ```

## Étape 2 : Installation

```bash
pip install -r requirements-client.txt
```

## Étape 3 : Lancement

```bash
streamlit run interface-streamlit.py
```

Ouvrez : http://localhost:8501

## Support

Email : support@votre-entreprise.com
Tél : +33 X XX XX XX XX
```

---

## 🔒 Protections Supplémentaires

### 1. Obfuscation du Code Backend (optionnel)

```bash
# Rendre le code Python illisible
pip install pyarmor
pyarmor obfuscate backend/app.py
```

### 2. Rate Limiting par IP

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("10/minute")  # Max 10 requêtes/minute par IP
async def chat(request: Request, ...):
    ...
```

### 3. Monitoring des Abus

```python
# Alertes si usage suspect
if usage_tracker[api_key]["count"] > 500 in 1 hour:
    send_alert_email(f"Usage suspect pour {api_key}")
```

---

## 💡 Résumé

**✅ CE QUE LE CLIENT REÇOIT :**
- Interface Streamlit (code visible mais inutile sans backend)
- 1 API Key unique
- Documentation d'installation
- Licence d'utilisation

**🔒 CE QUI RESTE SECRET :**
- Code backend (FastAPI, RAG, ChromaDB)
- Base de données vectorielle
- Vos documents source
- Clé API Groq
- Algorithmes de traitement

**💰 REVENUS RÉCURRENTS :**
- Abonnement mensuel
- Contrôle total des accès
- Évolutivité facile
- Pas de piratage possible

**🎯 POUR DÉBUTER :**
1. Déployez le backend sur Render.com (gratuit)
2. Créez le package client simplifié
3. Testez avec un premier client
4. Scaling progressif
