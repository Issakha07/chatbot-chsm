# Script de Génération du Package Client
# Crée un dossier client prêt à envoyer (sans dupliquer dans le repo)

$clientName = Read-Host "Nom du client (ex: hopital-xyz)"
$plan = Read-Host "Plan (demo/starter/business/enterprise)"
$email = Read-Host "Email du client"

# Générer la clé API
$randomPart = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$apiKey = "sk_${plan}_${randomPart}"

Write-Host "`n✅ Clé API générée: $apiKey" -ForegroundColor Green

# Créer le dossier client en DEHORS du repo Git
$clientDir = "J:\Stage-Hopital\clients-packages\chatbot-client-$clientName"
New-Item -ItemType Directory -Force -Path $clientDir | Out-Null

Write-Host "📦 Création du package dans: $clientDir" -ForegroundColor Cyan

# Créer interface-streamlit.py (version client)
$interfaceContent = @"
# -*- coding: utf-8 -*-
"""
IT Support Chatbot - Interface Client
Version simplifiée pour les clients (sans backend local)
Se connecte à l'API hébergée
"""

import streamlit as st
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="IT Support Chatbot 🏥",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration API
API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/chat")
API_KEY = os.getenv("API_KEY")
API_TIMEOUT = 30

if not API_KEY or API_KEY == "your_api_key_here":
    st.error("⚠️ Configuration manquante! Veuillez configurer votre fichier .env")
    st.stop()

# Charger CSS si disponible
try:
    with open("style.css", "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Initialisation session
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Bonjour! 👋 Je suis votre assistant IT Support.",
        "timestamp": datetime.now(),
        "sources": []
    }]
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()

def send_message(question: str) -> dict:
    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
    payload = {"question": question, "session_id": st.session_state.session_id}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data.get("session_id")
            return data
        elif response.status_code == 403:
            st.error("❌ API Key invalide")
        elif response.status_code == 429:
            st.error(f"⚠️ {response.json().get('detail', 'Quota dépassé')}")
        else:
            st.error(f"❌ Erreur serveur: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
    return None

# Header
st.markdown('<div class="main-header"><h1>🏥 IT Support Chatbot</h1></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Session")
    st.metric("Questions", st.session_state.request_count)
    st.divider()
    if st.button("🔄 Nouvelle conversation", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Nouvelle conversation démarrée!",
            "timestamp": datetime.now(),
            "sources": []
        }]
        st.session_state.session_id = None
        st.rerun()

# Messages
for msg in st.session_state.messages:
    role = "user-message" if msg["role"] == "user" else "assistant-message"
    icon = "👤" if msg["role"] == "user" else "🤖"
    st.markdown(f'<div class="{role}"><b>{icon}</b> {msg["content"]}</div>', unsafe_allow_html=True)
    if msg.get("sources"):
        st.caption(f"📚 Sources: {', '.join(msg['sources'])}")

# Input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Votre question:", max_chars=500, label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("📤", use_container_width=True)

if submit and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": datetime.now(), "sources": []})
    with st.spinner("🤔 Recherche..."):
        response = send_message(user_input)
    if response:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.get("answer", "Erreur"),
            "timestamp": datetime.now(),
            "sources": response.get("sources", [])
        })
        st.session_state.request_count += 1
    st.rerun()
"@

Set-Content -Path "$clientDir\interface-streamlit.py" -Value $interfaceContent -Encoding UTF8

# Copier le CSS depuis le projet principal
Copy-Item "style.css" "$clientDir\style.css"

# Créer .env avec la clé du client
$envContent = @"
# Configuration du Client - Chatbot IT Support

# URL de l'API backend (fournie par votre fournisseur)
BACKEND_API_URL=https://votre-api.onrender.com/api/chat

# Votre clé API unique
API_KEY=$apiKey
"@

Set-Content -Path "$clientDir\.env" -Value $envContent -Encoding UTF8

# Créer requirements.txt minimal
$requirementsContent = @"
# Dépendances client (version minimale)
streamlit==1.28.2
requests==2.31.0
python-dotenv==1.0.0
"@

Set-Content -Path "$clientDir\requirements.txt" -Value $requirementsContent -Encoding UTF8

# Créer README.md
$readmeContent = @"
# IT Support Chatbot - Guide d'Installation

## Installation Rapide

1. **Installer Python 3.8+**

2. **Créer environnement virtuel:**
``````powershell
python -m venv venv
venv\Scripts\Activate.ps1
``````

3. **Installer dépendances:**
``````powershell
pip install -r requirements.txt
``````

4. **Lancer l'application:**
``````powershell
streamlit run interface-streamlit.py
``````

Ouvrez: **http://localhost:8501**

## Configuration

Votre clé API est déjà configurée dans le fichier `.env`

**NE PARTAGEZ JAMAIS VOTRE CLÉ API!**

## Support

Email: support@votre-entreprise.com
"@

Set-Content -Path "$clientDir\README.md" -Value $readmeContent -Encoding UTF8

# Créer le fichier de clé API pour référence
$apiKeyFileContent = @"
================================================================================
CLÉ API - $clientName
================================================================================

Client: $email
Plan: $plan
Clé API: $apiKey

Date de création: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

⚠️ CONFIDENTIEL - Ne partagez pas cette clé
================================================================================
"@

Set-Content -Path "$clientDir\API_KEY.txt" -Value $apiKeyFileContent -Encoding UTF8

# Créer un ZIP
$zipPath = "J:\Stage-Hopital\clients-packages\chatbot-client-$clientName.zip"
Compress-Archive -Path "$clientDir\*" -DestinationPath $zipPath -Force

Write-Host "`n✅ Package client créé avec succès!" -ForegroundColor Green
Write-Host "📁 Dossier: $clientDir" -ForegroundColor Cyan
Write-Host "📦 ZIP: $zipPath" -ForegroundColor Cyan
Write-Host "`n🔑 Clé API: $apiKey" -ForegroundColor Yellow
Write-Host "`n📝 PROCHAINES ÉTAPES:" -ForegroundColor Magenta
Write-Host "1. Ajoutez la clé dans backend/app.py:"
Write-Host "   VALID_API_KEYS = {"
Write-Host "       `"$clientName`": `"$apiKey`","
Write-Host "   }"
Write-Host "2. Commit et push pour redéployer"
Write-Host "3. Envoyez le ZIP au client"
Write-Host "4. Facturez selon le plan: $plan`n"
