# Guide d'utilisation DVC pour le Chatbot CHSM

## 🎯 Objectif

Gérer les versions de vos documents et de la base vectorielle ChromaDB comme du code source avec Git.

## 📦 Installation et Configuration

### 1. Installer DVC

```powershell
venv\Scripts\Activate.ps1
pip install dvc dvc-gdrive  # ou dvc-s3, dvc-azure selon votre stockage
```

### 2. Initialiser DVC

```powershell
dvc init
```

Cela crée :
- `.dvc/` → Configuration DVC
- `.dvcignore` → Fichiers ignorés par DVC

### 3. Configurer le stockage distant (Remote)

#### Option A : Google Drive (Gratuit, facile)

```powershell
dvc remote add -d storage gdrive://1a2b3c4d5e6f7g8h9i0j
```

#### Option B : Stockage local (pour tests)

```powershell
dvc remote add -d storage J:\DVC-Storage\chatbot-chsm
```

#### Option C : AWS S3 (Production)

```powershell
dvc remote add -d storage s3://my-bucket/chatbot-chsm
dvc remote modify storage region eu-west-1
```

## 🚀 Workflow Quotidien

### Scénario 1 : Ajouter un nouveau document

```powershell
# 1. Copiez le nouveau PDF
cp "nouveau-document.pdf" documents/

# 2. Réindexez ChromaDB
python scripts/reindex_documents.py --mode incremental

# 3. Ajoutez documents/ et chroma_db/ à DVC
dvc add documents/
dvc add chroma_db/

# 4. Commitez les pointeurs DVC (pas les fichiers!)
git add documents.dvc chroma_db.dvc .gitignore
git commit -m "feat: Ajout nouveau-document.pdf"

# 5. Pushez les données vers le remote
dvc push

# 6. Pushez le commit Git
git push origin main
```

### Scénario 2 : Récupérer les données sur un autre PC

```powershell
# 1. Clonez le repo Git
git clone https://github.com/Issakha07/chatbot-chsm.git
cd chatbot-chsm

# 2. Récupérez les données DVC
dvc pull

# 3. Installez les dépendances
pip install -r requirements.txt

# 4. Lancez le chatbot
streamlit run interface-streamlit.py
```

### Scénario 3 : Revenir à une version précédente

```powershell
# 1. Listez les commits
git log --oneline

# 2. Revenez à un commit spécifique
git checkout <commit-hash> documents.dvc

# 3. Récupérez les anciennes données
dvc checkout documents.dvc

# 4. Réindexez avec les anciens documents
python scripts/reindex_documents.py --mode full
```

## 📊 Commandes Utiles

### Vérifier le statut

```powershell
dvc status  # Changements non trackés
git status  # Changements Git
```

### Comparer les versions

```powershell
dvc diff  # Différences de données entre commits
```

### Lister les fichiers trackés

```powershell
dvc list . --dvc-only
```

### Supprimer le cache local

```powershell
dvc gc --workspace  # Garde seulement la version actuelle
```

## 🔄 Automatisation avec GitHub Actions

Créez `.github/workflows/reindex.yml` :

```yaml
name: Auto Reindex

on:
  push:
    paths:
      - 'documents/**'
      - 'documents.dvc'

jobs:
  reindex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Pull data from DVC
        run: dvc pull documents.dvc
      
      - name: Reindex documents
        run: python scripts/reindex_documents.py --mode incremental
      
      - name: Push updated ChromaDB
        run: |
          dvc add chroma_db/
          git add chroma_db.dvc
          git commit -m "chore: Auto-reindex ChromaDB"
          dvc push
          git push
```

## 📁 Structure Recommandée

```
chatbot-chsm/
├── documents/              ← Tracké par DVC
│   ├── doc1.pdf
│   └── doc2.pdf
├── documents.dvc           ← Pointeur Git vers documents/
├── chroma_db/              ← Tracké par DVC
│   └── *.parquet
├── chroma_db.dvc           ← Pointeur Git vers chroma_db/
├── .dvc/
│   ├── config              ← Config DVC
│   └── .gitignore
├── scripts/
│   ├── reindex_documents.py
│   └── monitor_chatbot.py
└── .gitignore              ← Ignore documents/ et chroma_db/
```

## ⚠️ Bonnes Pratiques

### 1. **Ne jamais commiter les gros fichiers dans Git**

```gitignore
# .gitignore
documents/
chroma_db/
*.pdf
*.parquet
```

### 2. **Toujours pusher DVC après Git**

```powershell
# ❌ MAUVAIS
git push
dvc push  # Si cela échoue, le repo Git pointe vers des données inexistantes

# ✅ BON
dvc push  # D'abord les données
git push  # Ensuite le code
```

### 3. **Vérifier avant de push**

```powershell
dvc status  # Doit être vide
git status  # Doit montrer seulement *.dvc
dvc push --dry-run  # Simuler le push
```

## 🎓 Ressources

- [Documentation DVC](https://dvc.org/doc)
- [DVC avec Google Drive](https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive)
- [DVC Pipelines](https://dvc.org/doc/user-guide/pipelines)
