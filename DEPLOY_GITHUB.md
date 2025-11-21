# 🚀 GUIDE DE DÉPLOIEMENT GITHUB

## ✅ Nettoyage effectué - Projet prêt !

Votre projet a été nettoyé et optimisé pour GitHub. Voici ce qui a été fait :

### 🗑️ Suppressions (14 fichiers)
- ✅ `interface-streamlit.py` (ancienne version) → Remplacé par version actuelle
- ✅ `backend/app.py` (ancienne version) → Remplacé par version actuelle
- ✅ `run_backend.ps1`, `run_backend_noreload.ps1`, `run_frontend.ps1` (obsolètes)
- ✅ 7 fichiers de documentation de développement internes
- ✅ 2 scripts de test (`index_documents.py`, `test_indexing.py`)
- ✅ Logs et cache Python

### 📝 Fichiers renommés
- ✅ `backend/app_new.py` → `backend/app.py`
- ✅ `interface-streamlit-new.py` → `interface-streamlit.py`

### ➕ Fichiers ajoutés
- ✅ `.env.example` - Template sécurisé pour la configuration
- ✅ `.gitignore` complet - Protection contre les fichiers sensibles
- ✅ `CLEANUP_REPORT.md` - Documentation du nettoyage

---

## 📦 Structure finale

```
chatbot-chsm/
├── .github/
│   └── workflows/           # CI/CD (déjà configuré)
├── .streamlit/
│   └── config.toml          # Config Streamlit (évite boucles infinies)
├── backend/
│   ├── app.py              # ✅ Backend Groq + ChromaDB
│   └── document_processor.py # ✅ Multi-format documents
├── documents/
│   └── SERVICE-REQUESTS.pdf # Base de connaissances
├── .env.example            # ✅ Template configuration
├── .gitignore              # ✅ Sécurité complète
├── CHANGELOG.md            # Historique versions
├── CLEANUP_REPORT.md       # Rapport nettoyage
├── interface-streamlit.py  # ✅ Frontend Streamlit
├── QUICK_START.md          # Guide démarrage rapide
├── README.md               # Documentation principale
├── requirements.txt        # Dépendances Python
├── runtime.txt             # Version Python
├── start.ps1               # ✅ Script démarrage principal
└── START_CHATBOT.ps1       # ✅ Script alternatif
```

---

## 🔒 Vérification de sécurité

### ⚠️ CRITIQUE : Vérifiez que `.env` n'est PAS commité

```powershell
# 1. Vérifiez le statut Git
git status

# La sortie ne doit PAS montrer .env en vert
# Si .env apparaît, c'est DANGEREUX !
```

### ✅ Testez le .gitignore

```powershell
# Cette commande doit afficher : ".gitignore:4:.env    .env"
git check-ignore -v .env

# Si aucune sortie → .env n'est pas ignoré → DANGER !
```

---

## 🎯 Commandes Git pour déployer

### 1️⃣ Vérifiez ce qui sera commité

```powershell
cd "J:\Stage-Hopital\stage\chatbot-chsm"

# Voir tous les fichiers qui seront ajoutés
git status

# Vérifiez que ces fichiers NE SONT PAS listés :
# ❌ .env
# ❌ venv/
# ❌ __pycache__/
# ❌ *.log
# ❌ chroma_db/
```

### 2️⃣ Ajoutez les fichiers propres

```powershell
# Ajouter tous les fichiers (le .gitignore protège automatiquement)
git add .

# Vérifiez encore une fois
git status
```

### 3️⃣ Commitez avec un message clair

```powershell
git commit -m "🎉 Version production - Chatbot IT Support CHSM

✨ Fonctionnalités:
- Backend Groq API (LLM gratuit et rapide)
- ChromaDB (base vectorielle locale)
- Frontend Streamlit moderne et responsive
- Support multi-formats (PDF, Word, Excel, etc.)
- Détection automatique de langue (FR/EN)
- Prompt strict anti-hors-sujet

🔒 Sécurité:
- .env exclu du repo
- .env.example fourni comme template
- .gitignore complet

📚 Documentation:
- README.md complet
- QUICK_START.md pour démarrage rapide
- CHANGELOG.md pour suivi versions
- Scripts PowerShell pour Windows"
```

### 4️⃣ Poussez sur GitHub

```powershell
# Si première fois sur ce repo
git branch -M main
git remote add origin https://github.com/Issakha07/StageTI.git

# Poussez
git push -u origin main

# Ou si déjà configuré
git push
```

---

## 📝 Après le déploiement

### 1️⃣ Ajoutez des badges dans README.md

```markdown
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red)
![License](https://img.shields.io/badge/License-MIT-green)
```

### 2️⃣ Créez une release GitHub

1. Allez sur votre repo GitHub
2. Cliquez sur "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Titre: `Version 1.0.0 - Chatbot IT Support CHSM`
5. Description: Copiez depuis CHANGELOG.md

### 3️⃣ Configurez les GitHub Secrets (pour CI/CD)

Si vous utilisez GitHub Actions, ajoutez :
- `GROQ_API_KEY` dans Settings → Secrets → Actions

### 4️⃣ Activez les Issues et Discussions

- Settings → Features → ✅ Issues, ✅ Discussions

---

## ⚠️ En cas de problème

### Si `.env` a été commité par erreur

```powershell
# 1. Supprimez .env de l'historique Git
git filter-branch --force --index-filter `
  "git rm --cached --ignore-unmatch .env" `
  --prune-empty --tag-name-filter cat -- --all

# 2. Forcez le push (ATTENTION: action irréversible)
git push origin --force --all

# 3. Changez IMMÉDIATEMENT votre clé API Groq !
# https://console.groq.com/keys
```

### Si des fichiers sensibles apparaissent

```powershell
# Ajoutez-les dans .gitignore
echo "fichier_sensible.txt" >> .gitignore

# Supprimez du cache Git
git rm --cached fichier_sensible.txt

# Commitez
git commit -m "🔒 Ajout fichier sensible au .gitignore"
git push
```

---

## 🎉 Checklist finale

Avant de pousser sur GitHub, vérifiez :

- [ ] ✅ `.env` est dans `.gitignore`
- [ ] ✅ `.env.example` existe et est à jour
- [ ] ✅ `venv/` n'est pas commité
- [ ] ✅ `__pycache__/` n'est pas commité
- [ ] ✅ `chroma_db/` n'est pas commité (sera créé localement)
- [ ] ✅ Aucun fichier `.log` n'est commité
- [ ] ✅ README.md est à jour et complet
- [ ] ✅ QUICK_START.md explique le démarrage
- [ ] ✅ CHANGELOG.md documente la version
- [ ] ✅ requirements.txt contient toutes les dépendances
- [ ] ✅ Les scripts `start.ps1` et `START_CHATBOT.ps1` fonctionnent
- [ ] ✅ Le chatbot fonctionne localement avant push
- [ ] ✅ Pas de clés API en dur dans le code
- [ ] ✅ Pas de mots de passe dans le code
- [ ] ✅ Pas de données sensibles dans les documents/

---

## 🚀 Commande rapide tout-en-un

```powershell
# Exécutez cette commande pour tout faire d'un coup
git add . ; `
git status ; `
Write-Host "`n⚠️ VÉRIFIEZ que .env n'apparaît PAS ci-dessus !`n" -ForegroundColor Yellow ; `
Read-Host "Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler" ; `
git commit -m "🎉 Version production chatbot CHSM" ; `
git push
```

---

## 📞 Support

- **Email**: it-support@hopital.qc.ca
- **Téléphone**: Poste 5555
- **Issues GitHub**: https://github.com/Issakha07/StageTI/issues

---

**✨ Votre projet est prêt pour GitHub ! Bonne chance ! 🚀**
