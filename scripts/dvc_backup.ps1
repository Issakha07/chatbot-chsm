# Script de backup automatique DVC
# Sauvegarde les donnees vers le stockage distant

param(
    [switch]$Force = $false
)

$ProjectRoot = "J:\Stage-Hopital\stage\chatbot-chsm"
$LogFile = "$ProjectRoot\dvc_backup.log"

# Fonction de logging
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

Write-Log "[START] Demarrage du backup DVC automatique"

# Changer de repertoire
Set-Location $ProjectRoot
Write-Log "[INFO] Repertoire: $ProjectRoot"

# Verifier le statut DVC
Write-Log "[INFO] Verification du statut DVC..."
try {
    $status = dvc status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "[INFO] Statut DVC: $status"
    }
} catch {
    Write-Log "[ERROR] Erreur verification statut DVC: $_"
}

# Push vers le stockage distant
Write-Log "[INFO] Push vers le stockage distant..."
try {
    if ($Force) {
        dvc push --force
    } else {
        dvc push
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "[SUCCESS] Backup DVC reussi"
    } else {
        Write-Log "[ERROR] Erreur lors du push DVC (code: $LASTEXITCODE)"
        exit 1
    }
} catch {
    Write-Log "[ERROR] Erreur push DVC: $_"
    exit 1
}

# Nettoyer le cache local (optionnel)
Write-Log "[INFO] Nettoyage du cache local..."
try {
    dvc gc --workspace
    Write-Log "[SUCCESS] Cache nettoye"
} catch {
    Write-Log "[WARN] Erreur nettoyage cache: $_"
}

# Statistiques
Write-Log "[INFO] Verification des fichiers trackes..."
try {
    $tracked = dvc list . --dvc-only
    Write-Log "[INFO] Fichiers trackes: $tracked"
} catch {
    Write-Log "[WARN] Erreur liste fichiers: $_"
}

Write-Log "[SUCCESS] Backup DVC termine avec succes"
