# Configuration Google Drive pour DVC - Guide Pas a Pas

## Etape 1: Creer un dossier Google Drive

1. Allez sur https://drive.google.com
2. Connectez-vous avec votre compte Google
3. Creez un nouveau dossier: **Chatbot-CHSM-DVC**
4. Clic droit sur le dossier → Partager
5. Configurez les permissions (optionnel: partagez avec votre equipe)

## Etape 2: Obtenir l'ID du dossier

1. Ouvrez le dossier que vous venez de creer
2. Regardez l'URL dans la barre d'adresse:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                          ^^^^^^^^^^^^^^^^^^^^^^^
                                          C'est votre FOLDER_ID
   ```
3. Copiez cet ID (exemple: `1a2b3c4d5e6f7g8h9i0j`)

## Etape 3: Configurer DVC

Executez cette commande en remplacant FOLDER_ID par votre ID:

```powershell
dvc remote add -d gdrive gdrive://VOTRE_FOLDER_ID
dvc remote modify gdrive gdrive_acknowledge_abuse true
```

Exemple concret:
```powershell
dvc remote add -d gdrive gdrive://1a2b3c4d5e6f7g8h9i0j
dvc remote modify gdrive gdrive_acknowledge_abuse true
```

## Etape 4: Verifier la configuration

```powershell
dvc remote list
```

Vous devriez voir:
```
gdrive  gdrive://VOTRE_FOLDER_ID (default)
```

## Etape 5: Premiere synchronisation

```powershell
dvc push
```

DVC va:
1. Ouvrir votre navigateur
2. Demander l'autorisation d'acceder a Google Drive
3. Cliquez sur "Autoriser"
4. DVC va ensuite uploader vos fichiers

## Etape 6: Tester la recuperation

Sur une autre machine ou apres avoir supprime le cache:

```powershell
dvc pull
```

## Commandes utiles

```powershell
# Voir le statut
dvc status

# Forcer le push
dvc push --force

# Voir les fichiers dans le remote
dvc list . --dvc-only

# Changer le remote par defaut
dvc remote default gdrive
```

## Troubleshooting

### Erreur d'authentification
```powershell
# Supprimer les credentials et reessayer
Remove-Item ~\.dvc\tmp\gdrive-user-credentials.json -ErrorAction SilentlyContinue
dvc push
```

### Probleme de permissions
- Verifiez que le dossier Google Drive est accessible
- Verifiez les permissions de partage

### Cache local plein
```powershell
# Nettoyer le cache local
dvc gc --workspace
```

IMPORTANT: Conservez bien votre FOLDER_ID, vous en aurez besoin pour configurer DVC sur d'autres machines!
