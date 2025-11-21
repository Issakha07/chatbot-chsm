# Documentation API - IT Support Chatbot

## Vue d'ensemble

L'API IT Support Chatbot fournit des endpoints RESTful pour interagir avec un assistant intelligent basé sur Groq et ChromaDB.

**Base URL**: `http://localhost:8000`

**Version**: 3.0.0

---

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Streamlit)   │
└────────┬────────┘
         │ HTTP/JSON
         ▼
┌─────────────────────────────────┐
│   Backend API (FastAPI)         │
│   ┌──────────────────────────┐  │
│   │  Session Management      │  │
│   │  Rate Limiting           │  │
│   │  Validation              │  │
│   └──────────────────────────┘  │
│   ┌──────────────────────────┐  │
│   │  Document Search (RAG)   │  │
│   │  - ChromaDB              │  │
│   │  - Embeddings Cache      │  │
│   └──────────────────────────┘  │
│   ┌──────────────────────────┐  │
│   │  Response Generation     │  │
│   │  - Groq API (Llama 3.3)  │  │
│   └──────────────────────────┘  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   ChromaDB      │
│   (Vector Store)│
└─────────────────┘
```

---

## Endpoints

### 1. GET `/`

Endpoint racine pour obtenir les informations sur l'API.

**Réponse**:
```json
{
  "service": "IT Support Chatbot API",
  "version": "3.0.0",
  "status": "running",
  "model": "llama-3.3-70b-versatile",
  "documents_indexed": 42,
  "endpoints": {
    "chat": "/api/chat",
    "health": "/api/health",
    "metrics": "/api/metrics",
    "reset": "/api/reset/{session_id}",
    "reindex": "/api/reindex"
  }
}
```

---

### 2. GET `/api/health`

Vérification de l'état de santé de l'API.

**Réponse**:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-21T14:30:00.123456",
  "active_sessions": 5,
  "documents_count": 42
}
```

---

### 3. GET `/api/metrics`

Récupération des métriques de performance et d'utilisation.

**Réponse**:
```json
{
  "total_requests": 150,
  "successful_requests": 145,
  "failed_requests": 5,
  "success_rate": 96.67,
  "avg_response_time_seconds": 1.234,
  "cache_hit_rate": 35.5,
  "cache_hits": 53,
  "cache_misses": 97,
  "active_sessions": 5
}
```

**Utilisation pour monitoring**:
- Intégration avec Prometheus/Grafana
- Alertes sur `success_rate < 95%`
- Surveillance du `avg_response_time_seconds`

---

### 4. POST `/api/chat`

Endpoint principal pour interagir avec le chatbot.

**Corps de la requête**:
```json
{
  "question": "Comment réinitialiser mon mot de passe Windows?",
  "session_id": "abc123xyz456" // Optionnel
}
```

**Paramètres**:
- `question` (string, requis): Question de l'utilisateur (1-500 caractères)
- `session_id` (string, optionnel): ID de session pour maintenir le contexte

**Réponse**:
```json
{
  "answer": "Pour réinitialiser votre mot de passe Windows:\n1. Appuyez sur Ctrl+Alt+Suppr\n2. Cliquez sur 'Modifier un mot de passe'\n3. Suivez les instructions\n\nSi cela ne fonctionne pas, contactez le support au poste 5555.",
  "language": "fr",
  "sources": [
    "PASSWORD_RESET_GUIDE.pdf",
    "IT_SUPPORT_FAQ.docx"
  ],
  "session_id": "abc123xyz456"
}
```

**Codes d'erreur**:
- `422 Unprocessable Entity`: Question invalide ou contenu suspect
- `429 Too Many Requests`: Rate limiting (requête identique < 3s)
- `500 Internal Server Error`: Erreur serveur

**Exemples d'utilisation**:

#### Python (requests)
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"question": "Comment réinitialiser mon mot de passe?"}
)

data = response.json()
print(data["answer"])
```

#### JavaScript (fetch)
```javascript
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    question: "Comment réinitialiser mon mot de passe?"
  })
})
.then(res => res.json())
.then(data => console.log(data.answer));
```

#### cURL
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Comment réinitialiser mon mot de passe?"}'
```

---

### 5. POST `/api/reset/{session_id}`

Réinitialisation d'une session spécifique.

**Paramètres**:
- `session_id` (string, requis): ID de la session à réinitialiser

**Réponse**:
```json
{
  "message": "Session réinitialisée",
  "session_id": "abc123xyz456"
}
```

**Exemple**:
```bash
curl -X POST http://localhost:8000/api/reset/abc123xyz456
```

---

### 6. POST `/api/reindex`

Force la réindexation complète des documents.

**Réponse**:
```json
{
  "status": "success",
  "documents_indexed": 42
}
```

**Utilisation**:
- Après ajout de nouveaux documents
- En cas de corruption de l'index
- Pour mise à jour manuelle

**Exemple**:
```python
import requests

response = requests.post("http://localhost:8000/api/reindex")
print(f"Documents indexés: {response.json()['documents_indexed']}")
```

---

## Validation et Sécurité

### Validation des entrées

- **Longueur**: 1-500 caractères
- **Contenu suspect détecté**: `<script>`, `javascript:`, `DROP TABLE`, `DELETE FROM`
- **Rate limiting**: 3 secondes entre requêtes identiques

### Protection XSS et SQL Injection

Tous les inputs sont validés via Pydantic:
```python
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        dangerous = ['<script>', 'javascript:', 'DROP TABLE', 'DELETE FROM']
        if any(pattern.lower() in v.lower() for pattern in dangerous):
            raise ValueError("Contenu suspect détecté")
        return v
```

---

## Gestion des sessions

### Cycle de vie d'une session

1. **Création**: Automatique à la première requête
2. **Durée**: 2 heures d'inactivité
3. **Nettoyage**: Automatique des sessions expirées

### Historique conversationnel

- Stockage des 10 derniers échanges
- Maintien du contexte entre requêtes
- Utilisation pour génération de réponses contextuelles

---

## Performance et Optimisation

### Cache des embeddings

Le système cache les 100 requêtes les plus fréquentes:
```python
@lru_cache(maxsize=100)
def get_cached_embedding(query: str) -> tuple:
    """Cache les embeddings des requêtes fréquentes"""
    embedding = embedding_model.encode([query]).tolist()[0]
    return tuple(embedding)
```

**Impact**:
- Réduction de 60-80% du temps de réponse pour requêtes fréquentes
- Diminution de la charge CPU

### Logging structuré

Les logs sont générés en format JSON pour faciliter l'analyse:
```json
{
  "timestamp": "2024-11-21T14:30:00.123456",
  "level": "INFO",
  "message": "Chat request processed",
  "module": "app",
  "function": "chat",
  "session_id": "abc123xy",
  "duration": 1.234
}
```

---

## Exemples d'intégration

### Application Python

```python
import requests
from typing import Optional

class ChatbotClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def ask(self, question: str) -> dict:
        """Pose une question au chatbot"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "question": question,
                "session_id": self.session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data["session_id"]
            return data
        else:
            raise Exception(f"Erreur: {response.status_code}")
    
    def reset(self):
        """Réinitialise la conversation"""
        if self.session_id:
            requests.post(f"{self.base_url}/api/reset/{self.session_id}")
            self.session_id = None

# Utilisation
client = ChatbotClient()
response = client.ask("Comment réinitialiser mon mot de passe?")
print(response["answer"])
```

### Application Web (React)

```jsx
import { useState } from 'react';

function ChatBot() {
  const [sessionId, setSessionId] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const askQuestion = async () => {
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ question, session_id: sessionId })
    });
    
    const data = await response.json();
    setAnswer(data.answer);
    setSessionId(data.session_id);
  };

  return (
    <div>
      <input 
        value={question} 
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Posez votre question..."
      />
      <button onClick={askQuestion}>Envoyer</button>
      <div>{answer}</div>
    </div>
  );
}
```

---

## Variables d'environnement

Créez un fichier `.env` à la racine du projet:

```env
# Configuration Groq
GROQ_API_KEY=gsk_votre_clé_ici
GROQ_MODEL=llama-3.3-70b-versatile

# Configuration Documents
DOCUMENTS_DIR=./documents

# Environnement (development/production)
ENVIRONMENT=production
```

**En production**, `ENVIRONMENT=production` désactive le mode reload pour de meilleures performances.

---

## Déploiement

### Développement
```bash
cd backend
python app.py
```

### Production avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY documents/ ./documents/

ENV ENVIRONMENT=production

CMD ["python", "backend/app.py"]
```

---

## Monitoring en production

### Prometheus

Ajoutez l'exporteur de métriques:
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('chatbot_requests_total', 'Total requests')
response_time = Histogram('chatbot_response_seconds', 'Response time')

@app.middleware("http")
async def add_metrics(request, call_next):
    request_count.inc()
    with response_time.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Alertes recommandées

- `success_rate < 95%`: Problème de performance
- `avg_response_time > 5s`: Surcharge
- `cache_hit_rate < 20%`: Cache inefficace

---

## Support et Contact

- **Email**: it-support@hopital.qc.ca
- **Téléphone**: Poste 5555
- **Urgences**: Poste 9999

---

**Version**: 3.0.0  
**Dernière mise à jour**: 21 novembre 2024
