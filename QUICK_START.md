# 🚀 Démarrage Rapide

> **Note:** Ce guide est un résumé. Pour la documentation complète, consultez [README.md](README.md)

## ⚠️ Configuration Initiale

### 1. Clé API Groq (OBLIGATOIRE)

Éditez `.env` et ajoutez votre clé :

```env
GROQ_API_KEY=gsk_votre_clé_ici
```

**Obtenir une clé gratuite:** https://console.groq.com/keys

### 2. Installation

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🎯 Lancer le Chatbot

### Méthode Recommandée (Interface Streamlit)

**Terminal 1 - Backend:**
```powershell
venv\Scripts\Activate.ps1
python -m uvicorn backend.app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
venv\Scripts\Activate.ps1
streamlit run interface-streamlit.py
```

**Accès:** http://localhost:8501

---

## 📚 Ajouter des Documents

**Depuis l'interface Streamlit:**
1. Ouvrir la sidebar (⚙️ Actions Admin)
2. Cliquer sur "Parcourir" sous "Ajouter des documents"
3. Sélectionner vos PDFs
4. Cliquer "🔄 Sauvegarder & Réindexer"

**Manuellement:**
1. Copier les PDFs dans `documents/`
2. Redémarrer le backend

---

## 📊 Générer un Rapport

**Depuis l'interface:**
- Cliquer sur "📈 Générer rapport actuel" dans la sidebar
- Télécharger le rapport HTML généré

**En ligne de commande:**
```powershell
python scripts/monitor_chatbot.py
```

---

## 🛑 Arrêt

`Ctrl + C` dans les deux terminaux

---

## 📖 Documentation Complète

- **[README.md](README.md)** - Guide complet
- **[CONFIGURATION_COMPLETE.md](CONFIGURATION_COMPLETE.md)** - DVC, automation, monitoring
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentation API
- **[docs/](docs/)** - Guides détaillés (DVC, Evidently, etc.)
