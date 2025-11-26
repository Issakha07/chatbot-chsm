# 🗄️ Configuration du Stockage DVC Distant

## Options de Stockage Distant

### Option 1 : Stockage Local (Recommandé pour débuter)

```powershell
# Créer un dossier de stockage DVC local
mkdir J:\DVC-Storage\chatbot-chsm

# Configurer DVC pour utiliser ce dossier
dvc remote add -d local-storage J:\DVC-Storage\chatbot-chsm

# Vérifier la configuration
dvc remote list
```

**Avantages** : Simple, rapide, pas de configuration cloud
**Inconvénients** : Pas de sauvegarde externe, limité à votre machine

---

### Option 2 : Google Drive (Recommandé pour production)

#### Étape 1 : Installation de dvc[gdrive]
```powershell
pip install "dvc[gdrive]"
```

#### Étape 2 : Créer un dossier Google Drive
1. Allez sur [Google Drive](https://drive.google.com)
2. Créez un nouveau dossier : "Chatbot-CHSM-DVC"
3. Cliquez droit sur le dossier → "Obtenir le lien"
4. Copiez l'ID du dossier (partie après `/folders/`)

#### Étape 3 : Configurer DVC
```powershell
# Remplacez FOLDER_ID par l'ID copié
dvc remote add -d gdrive gdrive://FOLDER_ID

# Exemple:
# dvc remote add -d gdrive gdrive://1a2b3c4d5e6f7g8h9i0j

# Configurer l'authentification
dvc remote modify gdrive gdrive_acknowledge_abuse true
```

#### Étape 4 : Première synchronisation
```powershell
# DVC va ouvrir un navigateur pour l'authentification Google
dvc push
```

---

### Option 3 : Amazon S3

```powershell
# Installation
pip install "dvc[s3]"

# Configuration
dvc remote add -d s3storage s3://mon-bucket/chatbot-dvc

# Credentials AWS (dans .dvc/config.local - non versionné)
dvc remote modify s3storage access_key_id 'YOUR_ACCESS_KEY'
dvc remote modify s3storage secret_access_key 'YOUR_SECRET_KEY'
```

---

### Option 4 : Azure Blob Storage

```powershell
# Installation
pip install "dvc[azure]"

# Configuration
dvc remote add -d azure azure://moncontainer/chatbot-dvc

# Connection string
dvc remote modify azure connection_string 'YOUR_CONNECTION_STRING'
```

---

## 🔄 Workflow avec Stockage Distant

### 1. Tracker des données avec DVC
```powershell
# Ajouter les documents
dvc add documents/

# Ajouter la base ChromaDB
dvc add chroma_db/

# Commiter les fichiers .dvc
git add documents.dvc chroma_db.dvc .gitignore
git commit -m "chore: Track data with DVC"
```

### 2. Pousser vers le stockage distant
```powershell
# Envoyer les données au stockage distant
dvc push

# Pousser le code sur Git
git push origin main
```

### 3. Récupérer sur une autre machine
```powershell
# Cloner le repo
git clone https://github.com/Issakha07/chatbot-chsm.git
cd chatbot-chsm

# Télécharger les données depuis DVC
dvc pull
```

---

## 🎯 Commandes Utiles

```powershell
# Voir la configuration du remote
dvc remote list

# Modifier un remote
dvc remote modify <name> <option> <value>

# Supprimer un remote
dvc remote remove <name>

# Vérifier le statut
dvc status

# Voir les fichiers trackés
dvc list . --dvc-only

# Pousser seulement certains fichiers
dvc push documents.dvc

# Vérifier l'espace utilisé
dvc cache dir
```

---

## 🔒 Sécurité

### Fichier .dvc/config.local (NE JAMAIS COMMITER)

Pour les credentials sensibles :

```ini
[remote "s3storage"]
    access_key_id = YOUR_KEY
    secret_access_key = YOUR_SECRET
```

Ajoutez à `.gitignore` :
```
.dvc/config.local
```

---

## 📊 Monitoring de l'Espace

```powershell
# Taille du cache local
dvc cache dir | Measure-Object -Property Length -Sum

# Nettoyer le cache local (garde seulement les versions utilisées)
dvc gc --workspace

# Nettoyer agressivement
dvc gc --all-commits --cloud
```

---

## 🚨 Troubleshooting

### Erreur d'authentification Google Drive
```powershell
# Réinitialiser l'authentification
dvc remote modify gdrive gdrive_use_service_account false
dvc push --remote gdrive
```

### Problème de permissions
```powershell
# Vérifier les permissions du dossier
dvc remote modify gdrive gdrive_acknowledge_abuse true
```

### Cache corrompu
```powershell
# Supprimer et re-télécharger
Remove-Item -Recurse -Force .dvc/cache
dvc fetch
dvc checkout
```

---

## 📖 Ressources

- [DVC Remote Storage](https://dvc.org/doc/command-reference/remote)
- [Google Drive Setup](https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive)
- [AWS S3 Setup](https://dvc.org/doc/user-guide/data-management/remote-storage/amazon-s3)
