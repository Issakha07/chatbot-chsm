# -*- coding: utf-8 -*-
"""
IT Support Chatbot - Frontend Streamlit
Interface moderne avec historique conversationnel
Powered by Groq + ChromaDB
"""

import streamlit as st
import requests
from datetime import datetime
import time

# ==========================================
# 🎨 CONFIGURATION PAGE
# ==========================================
st.set_page_config(
    page_title="IT Support Chatbot 🏥",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔧 CONFIGURATION API
# ==========================================
import os
import subprocess
from pathlib import Path

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
API_URL = f"http://{BACKEND_HOST}:8000/api/chat"
API_RESET_URL = f"http://{BACKEND_HOST}:8000/api/reset"
API_TIMEOUT = 30

# Chemins scripts
SCRIPTS_DIR = Path(__file__).parent / "scripts"
REINDEX_SCRIPT = SCRIPTS_DIR / "reindex_documents.py"
MONITOR_SCRIPT = SCRIPTS_DIR / "monitor_chatbot.py"

# ==========================================
# 🎨 STYLES CSS
# ==========================================
# Charger les styles depuis le fichier CSS externe
with open("style.css", "r", encoding="utf-8") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# ==========================================
# 🔧 INITIALISATION SESSION
# ==========================================
def init_session():
    """Initialise l'état de session"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Bonjour! 👋 Je suis votre assistant IT Support. Comment puis-je vous aider aujourd'hui?",
                "timestamp": datetime.now(),
                "sources": []
            }
        ]
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    if "request_count" not in st.session_state:
        st.session_state.request_count = 0
    
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()

init_session()

# ==========================================
# 🛠️ FONCTIONS UTILITAIRES
# ==========================================
def format_time(dt: datetime) -> str:
    """Formate timestamp"""
    return dt.strftime("%H:%M")

def calculate_duration() -> str:
    """Calcule durée session"""
    delta = datetime.now() - st.session_state.session_start
    minutes = int(delta.total_seconds() / 60)
    seconds = int(delta.total_seconds() % 60)
    return f"{minutes}m {seconds}s"

def save_uploaded_files(uploaded_files) -> tuple[bool, str, int]:
    """Sauvegarder les fichiers uploadés dans le dossier documents"""
    try:
        documents_dir = Path("documents")
        documents_dir.mkdir(exist_ok=True)
        
        saved_count = 0
        for uploaded_file in uploaded_files:
            # Vérifier l'extension
            if not uploaded_file.name.lower().endswith('.pdf'):
                continue
            
            file_path = documents_dir / uploaded_file.name
            
            # Sauvegarder le fichier
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            saved_count += 1
        
        return True, f"✅ {saved_count} document(s) sauvegardé(s)", saved_count
    except Exception as e:
        return False, f"❌ Erreur sauvegarde: {str(e)}", 0

def reindex_documents() -> tuple[bool, str]:
    """Réindexer les documents"""
    try:
        result = subprocess.run(
            ["python", str(REINDEX_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return True, "✅ Documents réindexés avec succès!"
        else:
            return False, f"❌ Erreur lors de la réindexation: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "⏱️ Timeout: La réindexation a pris trop de temps"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def generate_report() -> tuple[bool, str, str]:
    """Générer le rapport Evidently"""
    try:
        result = subprocess.run(
            ["python", str(MONITOR_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            # Trouver le fichier de rapport le plus récent
            reports_dir = Path("reports")
            if reports_dir.exists():
                report_files = sorted(reports_dir.glob("chatbot_monitoring_*.html"), 
                                    key=lambda p: p.stat().st_mtime, 
                                    reverse=True)
                if report_files:
                    latest_report = report_files[0]
                    return True, "✅ Rapport généré avec succès!", str(latest_report)
            return True, "✅ Rapport généré!", ""
        else:
            return False, f"❌ Erreur génération rapport: {result.stderr}", ""
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}", ""

def send_message(question: str) -> dict:
    """Envoie message à l'API"""
    payload = {
        "question": question,
        "session_id": st.session_state.session_id
    }
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=API_TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data.get("session_id")
                return data
            
            elif response.status_code == 429:
                error = response.json().get("detail", "Trop de requêtes")
                st.error(f"⚠️ {error}")
                return None
            
            else:
                error = response.json().get("detail", "Erreur inconnue")
                st.error(f"❌ Erreur API ({response.status_code}): {error}")
                return None
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Timeout, nouvelle tentative ({attempt+2}/{max_retries})...")
                time.sleep(1)
                continue
            else:
                st.error("⏱️ La requête a expiré.")
                return None
        
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter à l'API. Vérifiez que le backend est lancé sur le port 8000.")
            return None
        
        except Exception as e:
            st.error(f"❌ Erreur inattendue: {str(e)}")
            return None
    
    return None

def reset_conversation():
    """Réinitialise la conversation"""
    try:
        if st.session_state.session_id:
            requests.post(
                f"{API_RESET_URL}/{st.session_state.session_id}",
                timeout=5
            )
    except:
        pass
    
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Conversation réinitialisée. Posez-moi vos questions IT! 🚀",
            "timestamp": datetime.now(),
            "sources": []
        }
    ]
    st.session_state.session_id = None
    st.session_state.request_count = 0
    st.session_state.session_start = datetime.now()
    st.rerun()

# ==========================================
# 🎨 INTERFACE
# ==========================================

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🏥 IT Support Chatbot</h1>
    <p>Assistant intelligent pour le support informatique hospitalier</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Statistiques de Session")
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{st.session_state.request_count}</div>
        <div class="stat-label">Questions</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{calculate_duration()}</div>
        <div class="stat-label">Durée</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Actions
    st.markdown("### ⚙️ Actions")
    
    if st.button("🔄 Nouvelle conversation", use_container_width=True, type="primary"):
        reset_conversation()
    
    if st.button("📥 Exporter l'historique", use_container_width=True):
        export = "=== HISTORIQUE CONVERSATION ===\n\n"
        for msg in st.session_state.messages:
            role = "VOUS" if msg["role"] == "user" else "ASSISTANT"
            export += f"[{format_time(msg['timestamp'])}] {role}:\n{msg['content']}\n"
            if msg.get("sources"):
                export += f"Sources: {', '.join(msg['sources'])}\n"
            export += "\n" + "="*50 + "\n\n"
        
        st.download_button(
            label="💾 Télécharger TXT",
            data=export,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.divider()
    
    # Actions administratives
    st.markdown("### ⚙️ Actions Admin")
    
    # Bouton 1: Upload et réindexation
    st.markdown("**📚 Ajouter des documents**")
    uploaded_files = st.file_uploader(
        "Sélectionner des fichiers PDF",
        type=['pdf'],
        accept_multiple_files=True,
        help="Téléchargez un ou plusieurs PDFs à ajouter à la base de connaissances",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.info(f"📄 {len(uploaded_files)} fichier(s) sélectionné(s)")
        
        col_upload1, col_upload2 = st.columns(2)
        
        with col_upload1:
            if st.button("💾 Sauvegarder", use_container_width=True):
                with st.spinner("⏳ Sauvegarde..."):
                    success, message, count = save_uploaded_files(uploaded_files)
                    if success and count > 0:
                        st.success(message)
                    elif success and count == 0:
                        st.warning("⚠️ Aucun fichier PDF valide")
                    else:
                        st.error(message)
        
        with col_upload2:
            if st.button("🔄 Sauvegarder & Réindexer", use_container_width=True, type="primary"):
                # Sauvegarder d'abord
                with st.spinner("⏳ Sauvegarde..."):
                    success, message, count = save_uploaded_files(uploaded_files)
                    
                if success and count > 0:
                    st.success(message)
                    # Puis réindexer
                    with st.spinner("⏳ Réindexation en cours..."):
                        success_reindex, message_reindex = reindex_documents()
                        if success_reindex:
                            st.success(message_reindex)
                            st.balloons()
                        else:
                            st.error(message_reindex)
                elif success and count == 0:
                    st.warning("⚠️ Aucun fichier PDF valide à réindexer")
                else:
                    st.error(message)
    
    st.divider()
    
    # Bouton 2: Générer rapport
    st.markdown("**📊 Rapport de performance**")
    
    if st.button("📈 Générer rapport actuel", use_container_width=True, help="Créer un rapport de performance avec toutes les conversations jusqu'à maintenant"):
        with st.spinner("⏳ Génération du rapport..."):
            success, message, report_path = generate_report()
            if success:
                st.success(message)
                if report_path and Path(report_path).exists():
                    st.info(f"📁 Rapport: `{Path(report_path).name}`")
                    # Lien pour ouvrir le rapport
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_html = f.read()
                        st.download_button(
                            label="📥 Télécharger le rapport",
                            data=report_html,
                            file_name=Path(report_path).name,
                            mime="text/html",
                            use_container_width=True
                        )
            else:
                st.error(message)
    
    st.divider()
    
    # Informations
    st.markdown("### ℹ️ Informations")
    st.markdown("""
    <div class="info-box">
    <strong>✨ Fonctionnalités:</strong><br>
    • 🌐 Bilingue FR/EN<br>
    • 📚 Base locale ChromaDB<br>
    • 💬 Historique contextuel<br>
    • 🔒 Sessions sécurisées
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ Limites:</strong><br>
    • Max 500 caractères/question<br>
    • Délai 3s entre doublons<br>
    • Timeout 30s par requête
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📞 Support Direct")
    st.info("""
    **Téléphone:** 📞 Poste 5555  
    **Email:** ✉️ it-support@hopital.qc.ca  
    **Urgences:** 🚨 Poste 9999
    """)
    
    # Version
    st.markdown("---")
    st.caption("Version 3.0.0 | Propulsé par Groq + ChromaDB")

# --- ZONE MESSAGES ---
st.markdown("### 💬 Conversation")

# Container scrollable
chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    👤 <strong>Vous</strong> • {format_time(msg['timestamp'])}
                </div>
                <div class="message-content">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    🤖 <strong>Assistant IT</strong> • {format_time(msg['timestamp'])}
                </div>
                <div class="message-content">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher sources si présentes
            if msg.get("sources") and len(msg["sources"]) > 0:
                sources_text = "<br>• ".join(msg["sources"])
                st.markdown(f"""
                <div class="sources-box">
                    📚 <strong>Sources consultées:</strong><br>
                    • {sources_text}
                </div>
                """, unsafe_allow_html=True)

# --- ZONE INPUT ---
st.divider()

# Formulaire de saisie
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Votre question:",
            placeholder="Ex: Comment réinitialiser mon mot de passe Windows?",
            label_visibility="collapsed",
            max_chars=500
        )
    
    with col2:
        submit = st.form_submit_button("Envoyer 📤", use_container_width=True, type="primary")

# Traitement
if submit and user_input:
    if len(user_input.strip()) == 0:
        st.warning("⚠️ Veuillez entrer une question.")
    
    else:
        # Ajouter message utilisateur
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now(),
            "sources": []
        })
        
        # Appeler API
        with st.spinner("🤔 Recherche en cours..."):
            response = send_message(user_input)
        
        if response:
            # Ajouter réponse
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("answer", "Erreur de réponse"),
                "timestamp": datetime.now(),
                "sources": response.get("sources", [])
            })
            
            st.session_state.request_count += 1
        
        # Rafraîchir
        st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem; padding: 1rem 0;">
    <p>🔒 <strong>Confidentialité:</strong> Vos conversations sont temporaires et sécurisées</p>
    <p>Développé avec ❤️ pour l'hôpital • Propulsé par Groq (Llama 3.3 70B)</p>
</div>
""", unsafe_allow_html=True)
