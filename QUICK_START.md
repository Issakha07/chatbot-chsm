# 🚀 Démarrage Rapide

## ⚠️ IMPORTANT - Configuration requise

### 1. Configurer votre clé API Groq

**Ouvrez le fichier `.env`** et remplacez la ligne :

```env
GROQ_API_KEY=your_groq_api_key_here
```

Par votre vraie clé API Groq :

```env
GROQ_API_KEY=gsk_votre_clé_ici_xxxxxxxxxxxxx
```

**Comment obtenir une clé Groq (GRATUIT) :**
1. Allez sur : https://console.groq.com/keys
2. Créez un compte (si nouveau)
3. Cliquez sur "Create API Key"
4. Copiez la clé et collez-la dans le fichier `.env`

---

## 🎯 Démarrer le chatbot

### Démarrage en deux terminaux

**Terminal 1 - Backend :**
```powershell
.\venv\Scripts\Activate.ps1
cd backend
python app.py
```

**Terminal 2 - Frontend :**
```powershell
.\venv\Scripts\Activate.ps1
streamlit run interface-streamlit.py
```

> **💡 Astuce :** Gardez les deux terminaux ouverts pendant l'utilisation du chatbot

---

## 🌐 Accéder au chatbot

Une fois démarré, ouvrez votre navigateur :

**Interface utilisateur :** http://localhost:8501

**API Backend :** http://localhost:8000

---

## 📚 Ajouter vos documents

1. Placez vos fichiers PDF dans le dossier `documents/`
2. Redémarrez le backend
3. Les documents seront automatiquement indexés

---

## 🛑 Arrêter le chatbot

Appuyez sur `Ctrl + C` dans les terminaux

---

## ❓ Problèmes courants

### "GROQ_API_KEY manquante"
→ Vérifiez que vous avez bien modifié le fichier `.env`

### "Module not found"
→ Réactivez l'environnement virtuel : `.\venv\Scripts\Activate.ps1`

### Le backend ne démarre pas
→ Vérifiez que le port 8000 n'est pas déjà utilisé

### Rien ne s'affiche dans le navigateur
→ Vérifiez que le backend est bien démarré sur le port 8000

---

## 📞 Support

Email : it-support@hopital.qc.ca  
Tel : Poste 5555
