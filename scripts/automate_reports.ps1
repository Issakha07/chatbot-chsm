# Script d'automatisation des rapports Evidently
# Genere un rapport quotidien et envoie une notification

param(
    [string]$ReportType = "daily",
    [switch]$SendEmail = $false
)

# Configuration
$ProjectRoot = "J:\Stage-Hopital\stage\chatbot-chsm"
$PythonExe = "$ProjectRoot\venv\Scripts\python.exe"
$MonitorScript = "$ProjectRoot\scripts\monitor_chatbot.py"
$ReportsDir = "$ProjectRoot\reports"
$LogFile = "$ProjectRoot\automation.log"

# Fonction de logging
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

# Debut du script
Write-Log "[START] Demarrage de l'automatisation Evidently - Type: $ReportType"

# Verifier que Python et le script existent
if (-not (Test-Path $PythonExe)) {
    Write-Log "[ERROR] Python introuvable a $PythonExe"
    exit 1
}

if (-not (Test-Path $MonitorScript)) {
    Write-Log "[ERROR] Script de monitoring introuvable a $MonitorScript"
    exit 1
}

# Changer de repertoire
Set-Location $ProjectRoot
Write-Log "[INFO] Repertoire de travail: $ProjectRoot"

# Generer le rapport
Write-Log "[INFO] Generation du rapport Evidently..."
try {
    & $PythonExe $MonitorScript
    Write-Log "[SUCCESS] Rapport genere avec succes"
}
catch {
    Write-Log "[ERROR] Erreur lors de la generation du rapport: $_"
    exit 1
}

# Trouver le dernier rapport genere
$LatestReport = Get-ChildItem -Path $ReportsDir -Filter "chatbot_monitoring_*.html" | 
Sort-Object LastWriteTime -Descending | 
Select-Object -First 1

if ($LatestReport) {
    Write-Log "[INFO] Dernier rapport: $($LatestReport.Name)"
    Write-Log "[INFO] Chemin: $($LatestReport.FullName)"
    
    # Optionnel: Ouvrir le rapport dans le navigateur
    if ($ReportType -eq "interactive") {
        Write-Log "[INFO] Ouverture du rapport dans le navigateur..."
        Start-Process $LatestReport.FullName
    }
    
    # Optionnel: Envoyer par email (necessite configuration SMTP)
    if ($SendEmail) {
        Write-Log "[INFO] Envoi du rapport par email..."
        # TODO: Implementer l'envoi d'email
    }
}
else {
    Write-Log "[WARN] Aucun rapport trouve dans $ReportsDir"
}

# Nettoyage des anciens rapports (garde les 30 derniers)
Write-Log "[INFO] Nettoyage des anciens rapports..."
$OldReports = Get-ChildItem -Path $ReportsDir -Filter "chatbot_monitoring_*.html" | 
Sort-Object LastWriteTime -Descending | 
Select-Object -Skip 30

if ($OldReports) {
    $OldReports | Remove-Item -Force
    Write-Log "[INFO] $($OldReports.Count) ancien(s) rapport(s) supprime(s)"
}
else {
    Write-Log "[INFO] Aucun ancien rapport a nettoyer"
}

Write-Log "[SUCCESS] Automatisation terminee avec succes"
