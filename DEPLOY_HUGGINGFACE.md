# 🚀 Déploiement sur Hugging Face Spaces

## ✅ Méthode recommandée: Import depuis GitHub

Cette méthode est la plus simple et synchronise automatiquement votre code GitHub avec Hugging Face.

### Étape 1: Créer un compte Hugging Face
- Allez sur https://huggingface.co/join
- Créez un compte gratuit (si pas déjà fait)

### Étape 2: Créer un nouveau Space
1. Allez sur https://huggingface.co/new-space
2. Remplissez les informations:
   - **Owner**: Votre nom d'utilisateur
   - **Space name**: `chatbot-it-support-chsm` (ou autre nom de votre choix)
   - **License**: MIT
   - **Select the Space SDK**: **Docker** ⚠️ IMPORTANT
   - **Visibility**: Public ou Private (selon vos besoins)

3. Cliquez sur **Create Space**

### Étape 3: Importer depuis GitHub

Une fois le Space créé:

1. Dans votre Space, allez dans **Files** 
2. Cliquez sur **⋮** (trois points) en haut à droite
3. Sélectionnez **Import from GitHub**
4. Connectez votre compte GitHub si demandé
5. Sélectionnez le repository: `Issakha07/chatbot-chsm`
6. Cliquez sur **Import**

Hugging Face va automatiquement:
- Cloner votre repository
- Détecter le `Dockerfile`
- Commencer à builder l'application

### Étape 4: Configurer la clé API Groq

**IMPORTANT**: Sans cette étape, le chatbot ne fonctionnera pas!

1. Dans votre Space, allez dans **Settings**
2. Descendez jusqu'à **Repository secrets**
3. Cliquez sur **New secret**
4. Remplissez:
   - **Name**: `GROQ_API_KEY`
   - **Value**: Votre clé API Groq complète (ex: `gsk_xxxxxxxxxxxxx`)
5. Cliquez sur **Add secret**

Le Space redémarrera automatiquement avec la clé API.

### Étape 5: Attendre le build

- Le build initial prend 5-10 minutes
- Vous pouvez suivre la progression dans l'onglet **Build logs**
- Une fois terminé, le Space affichera l'interface Streamlit

### Étape 6: Tester le chatbot

Votre chatbot est maintenant accessible à:
```
https://huggingface.co/spaces/VOTRE_USERNAME/chatbot-it-support-chsm
```

## 💡 Utilisation

1. Attendez le démarrage du Space (30-40 secondes au premier lancement)
2. Posez votre question dans la zone de texte
3. Le chatbot cherche dans la documentation et génère une réponse contextuelle
4. Utilisez le bouton "🔄 Nouvelle conversation" pour réinitialiser l'historique

**Astuce**: Partagez cette URL avec vos collègues!

---

## 🔄 Mises à jour automatiques

L'avantage de la méthode GitHub:
- Chaque fois que vous faites un `git push` sur GitHub
- Hugging Face détecte les changements
- Le Space se rebuild automatiquement
- Vos modifications sont déployées sans intervention manuelle

---

## 🆘 Dépannage

**Le Space ne démarre pas:**
- Vérifiez les logs dans l'onglet **Build logs**
- Assurez-vous que `GROQ_API_KEY` est bien configuré dans les Secrets
- Le premier build prend du temps (patience!)

**Erreur "API key manquante":**
- Vérifiez que le Secret est nommé exactement `GROQ_API_KEY` (sensible à la casse)
- Redémarrez le Space: Settings > Factory reboot

**Le chatbot ne répond pas:**
- Attendez 30-40 secondes au premier démarrage (chargement du modèle d'embeddings)
- Vérifiez dans les logs que le backend a bien démarré
- Assurez-vous que la clé Groq API est valide

**Erreur de build Docker:**
- Vérifiez que tous les fichiers sont bien sur GitHub (`Dockerfile`, `requirements.txt`, etc.)
- Consultez les Build logs pour voir l'erreur exacte
- Vérifiez que le `Dockerfile` principal (pas `Dockerfile.local`) est bien à la racine

---

## 📋 Fichiers importants

Voici les fichiers qui doivent être présents sur GitHub pour le déploiement:

```
chatbot-chsm/
├── Dockerfile              ← Pour Hugging Face Spaces (IMPORTANT!)
├── Dockerfile.local        ← Pour développement local uniquement
├── requirements.txt        ← Dépendances Python
├── interface-streamlit.py  ← Frontend
├── backend/
│   ├── app.py             ← Backend FastAPI
│   └── document_processor.py
├── documents/             ← Vos PDFs
│   └── SERVICE-REQUESTS.pdf
└── README_HUGGINGFACE.md  ← À renommer en README.md sur HF (optionnel)
```

---

## 🔧 Configuration des variables d'environnement

Dans **Settings > Variables and Secrets**:

| Variable | Valeur | Description |
|----------|--------|-------------|
| `GROQ_API_KEY` | votre_clé_api | **Secret** - Clé API Groq |
| `BACKEND_HOST` | `localhost` | **Variable** - Host du backend |

---

## 📝 Notes importantes

1. **Gratuit mais avec limites**:
   - CPU seulement (pas de GPU)
   - Le Space s'endort après 48h d'inactivité
   - Se réveille au premier accès (15-30 secondes)

2. **Pour usage production intensif**:
   - Envisagez un upgrade vers un Space persistant ($$$)
   - Ou utilisez Render.com / Railway.app

3. **Sécurité**:
   - Votre clé API Groq reste PRIVÉE dans les Secrets
   - Ne la partagez jamais dans le code
   - Le fichier `.env` local n'est jamais envoyé (bloqué par `.gitignore`)

---
