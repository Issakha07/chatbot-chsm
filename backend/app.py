# -*- coding: utf-8 -*-
"""
IT Support Chatbot - Backend FastAPI avec Groq + RAG Local
Base de connaissance vectorielle locale avec ChromaDB
"""

import os
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from contextlib import asynccontextmanager
from functools import lru_cache
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from groq import Groq

# Import du processeur de documents universel
try:
    from .document_processor import DocumentProcessor, chunk_text
except ImportError:
    from document_processor import DocumentProcessor, chunk_text

# Configuration langdetect
DetectorFactory.seed = 0

# Charger variables d'environnement
load_dotenv()

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "../documents")

# Limites de sécurité
MAX_QUESTION_LENGTH = 500
MAX_HISTORY_SIZE = 10
RATE_LIMIT_SECONDS = 3

# Métriques
metrics = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'total_response_time': 0.0,
    'cache_hits': 0,
    'cache_misses': 0
}

# ==========================================
# LOGGING STRUCTURÉ
# ==========================================

# Créer dossier logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
        return json.dumps(log_data)

json_handler = logging.FileHandler('chatbot.log')
json_handler.setFormatter(JSONFormatter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[json_handler, console_handler]
)
logger = logging.getLogger(__name__)

# ==========================================
# LOGGING CONVERSATIONS (POUR EVIDENTLY)
# ==========================================

def log_conversation(question: str, answer: str, response_time: float, 
                     language: str, sources: List[str], has_answer: bool):
    """Logger une conversation pour analyse Evidently"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "response_time": response_time,
        "language": language,
        "sources": sources,
        "has_answer": has_answer,
        "confidence": 0.85 if has_answer and sources else 0.5,
        "num_sources": len(sources)
    }
    
    # Ajouter au fichier du jour (format JSONL)
    log_file = LOG_DIR / f"chat_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# ==========================================
# INITIALISATION FASTAPI
# ==========================================

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gérer les événements de démarrage et arrêt"""
    # Startup
    logger.info("🚀 Démarrage API...")
    if collection.count() == 0:
        logger.info("Collection vide, indexation des documents...")
        index_documents()
    else:
        logger.info(f"Collection déjà indexée: {collection.count()} chunks")
    
    yield
    
    # Shutdown
    logger.info("🔌 Arrêt API...")

app = FastAPI(
    title="IT Support Chatbot API",
    description="Healthcare IT Support avec Groq + ChromaDB",
    version="3.0.0",
    lifespan=lifespan
)

# CORS pour Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🧠 INITIALISATION SERVICES
# ==========================================

# Client Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Modèle d'embeddings (léger et efficace)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Base vectorielle ChromaDB
chroma_client = chromadb.Client(Settings(
    persist_directory="../chroma_db",
    anonymized_telemetry=False
))

# Collection pour les documents
try:
    collection = chroma_client.get_collection("it_support_docs")
    logger.info("✅ Collection ChromaDB chargée")
except:
    collection = chroma_client.create_collection(
        name="it_support_docs",
        metadata={"hnsw:space": "cosine"}
    )
    logger.info("✅ Nouvelle collection ChromaDB créée")

# ==========================================
# 📦 MODÈLES PYDANTIC
# ==========================================
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_LENGTH)
    session_id: Optional[str] = None
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        v = v.strip()
        dangerous = ['<script>', 'javascript:', 'DROP TABLE', 'DELETE FROM']
        if any(pattern.lower() in v.lower() for pattern in dangerous):
            raise ValueError("Contenu suspect détecté")
        return v

class ChatResponse(BaseModel):
    answer: str
    language: str
    sources: List[str] = []
    session_id: str

# ==========================================
# 💾 GESTION SESSIONS
# ==========================================
sessions_store: Dict[str, Dict] = {}

def get_or_create_session(session_id: Optional[str]) -> tuple[str, Dict]:
    """Récupère ou crée une session utilisateur"""
    if not session_id or session_id not in sessions_store:
        session_id = os.urandom(16).hex()
        sessions_store[session_id] = {
            'chat_history': [],
            'last_question': None,
            'last_time': None,
            'created_at': datetime.now()
        }
        logger.info(f"Nouvelle session: {session_id[:8]}")
    return session_id, sessions_store[session_id]

def clean_old_sessions():
    """Nettoie sessions > 2h"""
    now = datetime.now()
    to_delete = [
        sid for sid, data in sessions_store.items()
        if (now - data['created_at']).total_seconds() > 7200
    ]
    for sid in to_delete:
        del sessions_store[sid]
    if to_delete:
        logger.info(f"Nettoyé {len(to_delete)} sessions")

# ==========================================
# 🌐 DÉTECTION DE LANGUE
# ==========================================
def detect_language(text: str) -> str:
    """Détecte la langue (fr/en)"""
    try:
        detected = detect(text.strip())
        return 'fr' if detected == 'fr' else 'en'
    except:
        return 'en'

# ==========================================
# 📚 INDEXATION DOCUMENTS (MULTI-FORMATS)
# ==========================================
def index_documents():
    """Indexe tous les documents du dossier documents/ (PDF, Word, Excel, TXT, etc.)"""
    # Résoudre le chemin absolu: backend/../documents = racine/documents
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    docs_path = project_root / "documents"
    
    if not docs_path.exists():
        logger.warning(f"Dossier {docs_path} introuvable")
        return
    
    # Initialiser le processeur universel
    processor = DocumentProcessor()
    
    # Traiter tous les fichiers supportés
    results = processor.process_directory(str(docs_path), recursive=False)
    
    if not results:
        logger.warning("Aucun document trouvé ou supporté")
        return
    
    logger.info(f"Indexation de {len(results)} documents...")
    
    total_chunks = 0
    for result in results:
        if not result['success']:
            logger.warning(f"❌ Échec: {Path(result['file_path']).name} - {result['error']}")
            continue
        
        file_name = Path(result['file_path']).name
        text = result['text']
        
        if not text or len(text) < 50:
            logger.warning(f"⚠️ Document trop court ignoré: {file_name}")
            continue
        
        # Découper en chunks
        chunks = chunk_text(text)
        logger.info(f"  → {file_name}: {len(chunks)} chunks créés")
        
        # Générer embeddings
        embeddings = embedding_model.encode(chunks).tolist()
        
        # Ajouter à ChromaDB
        ids = [f"{Path(result['file_path']).stem}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": file_name,
                "file_type": result['file_type'],
                "chunk_id": i
            } 
            for i in range(len(chunks))
        ]
        
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        total_chunks += len(chunks)
    
    # Afficher statistiques
    stats = processor.get_stats()
    logger.info(f"""
    ╔════════════════════════════════════════╗
    ║   INDEXATION TERMINÉE                  ║
    ╠════════════════════════════════════════╣
    ║ Documents traités: {stats['success']:3d}               ║
    ║ Échecs:            {stats['errors']:3d}               ║
    ║ Chunks totaux:     {total_chunks:5d}             ║
    ╚════════════════════════════════════════╝
    """)
    
    for doc_type, count in stats['by_type'].items():
        logger.info(f"  📄 {doc_type}: {count} fichier(s)")


# ==========================================
# RECHERCHE VECTORIELLE AVEC CACHE
# ==========================================
@lru_cache(maxsize=100)
def get_cached_embedding(query: str) -> tuple:
    """Cache les embeddings des requêtes fréquentes"""
    embedding = embedding_model.encode([query]).tolist()[0]
    return tuple(embedding)

def search_documents(query: str, top_k: int = 3) -> Dict:
    """Recherche dans ChromaDB avec cache"""
    try:
        # Générer embedding de la question (avec cache)
        try:
            query_embedding = list(get_cached_embedding(query))
            metrics['cache_hits'] += 1
        except:
            query_embedding = embedding_model.encode([query]).tolist()[0]
            metrics['cache_misses'] += 1
        
        # Recherche
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                documents.append({
                    'content': doc,
                    'source': metadata.get('source', 'Unknown'),
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        logger.info(f"Recherche: {len(documents)} documents trouvés")
        return {"documents": documents}
    
    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        return {"documents": []}

# ==========================================
# 🧠 GÉNÉRATION RÉPONSE GROQ
# ==========================================
def generate_answer(context: str, question: str, chat_history: List[Dict], user_lang: str) -> str:
    """Génère réponse avec Groq"""
    
    language_name = "French" if user_lang == "fr" else "English"
    
    system_prompt = f"""You are a SPECIALIZED hospital IT Support assistant with STRICT limitations.

🔒 ABSOLUTE RULES - YOU MUST FOLLOW THESE:
1. You can ONLY answer questions about IT support topics found in the provided context
2. If the question is NOT about IT support (computers, software, network, passwords, printers, etc.) → REFUSE to answer
3. If no relevant information exists in the context → Say you don't have that information in your knowledge base
4. NEVER answer questions about: medicine, health, personal advice, general knowledge, calculations, etc.
5. NEVER make up information - use ONLY what's in the context below

🌐 LANGUAGE RULE:
The user's question is in {language_name}. You MUST respond in {language_name}.
- If question is in French → respond in French
- If question is in English → respond in English
- NEVER mix languages

📋 RESPONSE STYLE:
- Clear and concise
- Use bullet points for step-by-step instructions
- Professional and courteous tone
- If refusing: politely explain you only handle IT support questions

📚 KNOWLEDGE BASE CONTEXT:
{context if context else "No relevant IT support information found in knowledge base."}

EXAMPLES OF VALID QUESTIONS:
✅ "Comment réinitialiser mon mot de passe?"
✅ "Mon imprimante ne fonctionne pas"
✅ "Je n'arrive pas à me connecter à Citrix"
✅ "How do I access the VPN?"

EXAMPLES OF INVALID QUESTIONS (REFUSE THESE):
❌ "Quelle est la capitale de la France?" → Medical/general knowledge
❌ "Comment traiter un patient?" → Medical question
❌ "Calcule 2+2" → Not IT support
❌ "Tell me a joke" → Not IT support
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Historique (5 derniers messages)
    for msg in chat_history[-5:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    messages.append({"role": "user", "content": question})
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=800,
            top_p=0.95
        )
        
        answer = chat_completion.choices[0].message.content.strip()
        logger.info(f"Réponse Groq générée: {len(answer)} caractères")
        return answer
    
    except Exception as e:
        logger.error(f"Erreur Groq: {e}")
        if user_lang == 'fr':
            return "Désolé, une erreur est survenue. Réessayez."
        return "Sorry, an error occurred. Please retry."

# ==========================================
# 🌐 ROUTES API
# ==========================================

@app.get("/")
async def root():
    """Page d'accueil API"""
    return {
        "service": "IT Support Chatbot API",
        "version": "3.0.0",
        "status": "running",
        "model": GROQ_MODEL,
        "documents_indexed": collection.count(),
        "endpoints": {
            "chat": "/api/chat",
            "health": "/api/health",
            "metrics": "/api/metrics",
            "reset": "/api/reset/{session_id}",
            "reindex": "/api/reindex"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions_store),
        "documents_count": collection.count()
    }

@app.get("/api/metrics")
async def get_metrics():
    """Endpoint de métriques pour monitoring"""
    avg_response_time = (
        metrics['total_response_time'] / metrics['successful_requests']
        if metrics['successful_requests'] > 0 else 0
    )
    
    cache_hit_rate = (
        metrics['cache_hits'] / (metrics['cache_hits'] + metrics['cache_misses'])
        if (metrics['cache_hits'] + metrics['cache_misses']) > 0 else 0
    )
    
    return {
        "total_requests": metrics['total_requests'],
        "successful_requests": metrics['successful_requests'],
        "failed_requests": metrics['failed_requests'],
        "success_rate": round(metrics['successful_requests'] / metrics['total_requests'] * 100, 2) if metrics['total_requests'] > 0 else 0,
        "avg_response_time_seconds": round(avg_response_time, 3),
        "cache_hit_rate": round(cache_hit_rate * 100, 2),
        "cache_hits": metrics['cache_hits'],
        "cache_misses": metrics['cache_misses'],
        "active_sessions": len(sessions_store)
    }

@app.post("/api/reindex")
async def reindex_documents():
    """Force réindexation des documents"""
    try:
        # Supprimer ancienne collection
        chroma_client.delete_collection("it_support_docs")
        
        # Recréer
        global collection
        collection = chroma_client.create_collection(
            name="it_support_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Réindexer
        index_documents()
        
        return {
            "status": "success",
            "documents_indexed": collection.count()
        }
    except Exception as e:
        logger.error(f"Erreur réindexation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """Endpoint principal du chatbot"""
    start_time = time.time()
    metrics['total_requests'] += 1
    
    try:
        clean_old_sessions()
        
        # Session
        session_id, session_data = get_or_create_session(request.session_id)
        
        question = request.question
        user_lang = detect_language(question)
        
        logger.info(f"[{session_id[:8]}] Question ({user_lang}): {question[:80]}")
        
        # Anti-doublon
        if session_data['last_question'] == question and session_data['last_time']:
            time_diff = (datetime.now() - session_data['last_time']).total_seconds()
            if time_diff < RATE_LIMIT_SECONDS:
                msg = ("Veuillez attendre quelques secondes." if user_lang == 'fr' 
                       else "Please wait a few seconds.")
                raise HTTPException(status_code=429, detail=msg)
        
        # Recherche documents
        search_results = search_documents(question)
        documents = search_results.get("documents", [])
        
        # Construire contexte
        if documents:
            context = "\n\n".join([
                f"[Source: {doc['source']}]\n{doc['content']}"
                for doc in documents[:3]
            ])
            sources = list(set([doc['source'] for doc in documents[:3]]))
        else:
            context = ""
            sources = []
        
        # Générer réponse
        if not context.strip():
            if user_lang == 'fr':
                answer = ("Je n'ai pas trouvé d'information pertinente. "
                         "Contactez le support au poste 5555.")
            else:
                answer = ("I couldn't find relevant information. "
                         "Contact support at extension 5555.")
        else:
            chat_history = session_data['chat_history']
            answer = generate_answer(context, question, chat_history, user_lang)
        
        # Mise à jour session
        session_data['chat_history'].append({"role": "user", "content": question})
        session_data['chat_history'].append({"role": "assistant", "content": answer})
        
        if len(session_data['chat_history']) > MAX_HISTORY_SIZE * 2:
            session_data['chat_history'] = session_data['chat_history'][-MAX_HISTORY_SIZE*2:]
        
        session_data['last_question'] = question
        session_data['last_time'] = datetime.now()
        
        # Métriques
        duration = time.time() - start_time
        metrics['successful_requests'] += 1
        metrics['total_response_time'] += duration
        
        # Log pour Evidently
        log_conversation(
            question=question,
            answer=answer,
            response_time=duration,
            language=user_lang,
            sources=sources,
            has_answer=len(answer) > 50 and "je n'ai pas" not in answer.lower()
        )
        
        # Log structuré
        log_record = logger.makeRecord(
            logger.name, logging.INFO, __file__, 0,
            f"Chat request processed", (), None
        )
        log_record.session_id = session_id[:8]
        log_record.duration = round(duration, 3)
        logger.handle(log_record)
        
        return ChatResponse(
            answer=answer,
            language=user_lang,
            sources=sources,
            session_id=session_id
        )
    
    except HTTPException:
        metrics['failed_requests'] += 1
        raise
    except Exception as e:
        metrics['failed_requests'] += 1
        logger.exception("Erreur interne")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.post("/api/reset/{session_id}")
async def reset_session(session_id: str):
    """Réinitialise une session"""
    if session_id in sessions_store:
        del sessions_store[session_id]
        logger.info(f"Session réinitialisée: {session_id[:8]}")
        return {"message": "Session réinitialisée", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session introuvable")

# ==========================================
# 🚀 DÉMARRAGE
# ==========================================
if __name__ == "__main__":
    import uvicorn
    
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY manquante")
        exit(1)
    
    logger.info("Démarrage IT Support Chatbot API (Groq + ChromaDB)")
    logger.info(f"Modèle: {GROQ_MODEL}")
    logger.info(f"Documents: {DOCUMENTS_DIR}")
    logger.info(f"Environnement: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Détection environnement
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=not is_production,  # Reload désactivé en production
        log_level="info"
    )
