# Script de configuration des taches planifiees Windows
# Configure l'automatisation complete du monitoring chatbot

param(
    [switch]$Remove = $false
)

$ProjectRoot = "J:\Stage-Hopital\stage\chatbot-chsm"
$PythonExe = "$ProjectRoot\venv\Scripts\python.exe"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Configuration Taches Planifiees - Chatbot" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour creer une tache
function Create-ChatbotTask {
    param(
        [string]$TaskName,
        [string]$Description,
        [string]$ScriptPath,
        [string]$Time,
        [string]$Trigger = "Daily"
    )
    
    Write-Host "[INFO] Creation de la tache: $TaskName" -ForegroundColor Yellow
    
    try {
        # Verifier si la tache existe deja
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Write-Host "[WARN] La tache $TaskName existe deja. Suppression..." -ForegroundColor Yellow
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        
        # Preparer l'action
        if ($ScriptPath -like "*.ps1") {
            # Script PowerShell
            $Action = New-ScheduledTaskAction -Execute "powershell.exe" `
                -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`"" `
                -WorkingDirectory $ProjectRoot
        }
        else {
            # Script Python
            $Action = New-ScheduledTaskAction -Execute $PythonExe `
                -Argument "`"$ScriptPath`"" `
                -WorkingDirectory $ProjectRoot
        }
        
        # Preparer le declencheur
        if ($Trigger -eq "Daily") {
            $TaskTrigger = New-ScheduledTaskTrigger -Daily -At $Time
        }
        elseif ($Trigger -eq "Hourly") {
            $TaskTrigger = New-ScheduledTaskTrigger -Once -At $Time -RepetitionInterval (New-TimeSpan -Hours 1)
        }
        
        # Parametres
        $Settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -RestartCount 3 `
            -RestartInterval (New-TimeSpan -Minutes 1)
        
        # Creer la tache
        Register-ScheduledTask `
            -TaskName $TaskName `
            -Action $Action `
            -Trigger $TaskTrigger `
            -Settings $Settings `
            -Description $Description `
            -User $env:USERNAME
        
        Write-Host "[OK] Tache $TaskName creee avec succes!" -ForegroundColor Green
        return $true
        
    }
    catch {
        Write-Host "[ERROR] Erreur creation tache $TaskName : $_" -ForegroundColor Red
        return $false
    }
}

# Fonction pour supprimer les taches
function Remove-ChatbotTasks {
    Write-Host "`n[INFO] Suppression des taches planifiees..." -ForegroundColor Yellow
    
    $tasks = @(
        "Chatbot-Evidently-Reports",
        "Chatbot-Quality-Alerts",
        "Chatbot-DVC-Backup"
    )
    
    foreach ($task in $tasks) {
        try {
            $existingTask = Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $task -Confirm:$false
                Write-Host "[OK] Tache $task supprimee" -ForegroundColor Green
            }
            else {
                Write-Host "[INFO] Tache $task inexistante" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "[ERROR] Erreur suppression $task : $_" -ForegroundColor Red
        }
    }
}

# Si mode suppression
if ($Remove) {
    Remove-ChatbotTasks
    Write-Host "`n[OK] Suppression terminee!" -ForegroundColor Green
    exit 0
}

# Verification des pre-requis
Write-Host "[INFO] Verification des pre-requis..." -ForegroundColor Yellow

if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python introuvable: $PythonExe" -ForegroundColor Red
    Write-Host "[INFO] Assurez-vous que l'environnement virtuel est cree" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "$ProjectRoot\scripts\automate_reports.ps1")) {
    Write-Host "[ERROR] Script automate_reports.ps1 introuvable" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$ProjectRoot\scripts\quality_alerts.py")) {
    Write-Host "[ERROR] Script quality_alerts.py introuvable" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Pre-requis OK" -ForegroundColor Green
Write-Host ""

# Creation des taches

# 1. Rapports Evidently (quotidien a 23h)
$success1 = Create-ChatbotTask `
    -TaskName "Chatbot-Evidently-Reports" `
    -Description "Generation automatique des rapports de monitoring Evidently" `
    -ScriptPath "$ProjectRoot\scripts\automate_reports.ps1" `
    -Time "23:00" `
    -Trigger "Daily"

# 2. Alertes Qualite (quotidien a 8h)
$success2 = Create-ChatbotTask `
    -TaskName "Chatbot-Quality-Alerts" `
    -Description "Verification de la qualite du chatbot et envoi d'alertes" `
    -ScriptPath "$ProjectRoot\scripts\quality_alerts.py" `
    -Time "08:00" `
    -Trigger "Daily"

# 3. Backup DVC (quotidien a 2h du matin)
$success3 = Create-ChatbotTask `
    -TaskName "Chatbot-DVC-Backup" `
    -Description "Sauvegarde automatique des donnees avec DVC" `
    -ScriptPath "$ProjectRoot\scripts\dvc_backup.ps1" `
    -Time "02:00" `
    -Trigger "Daily"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  RESUME DE LA CONFIGURATION" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

if ($success1) {
    Write-Host "[OK] Rapports Evidently: Quotidien a 23h00" -ForegroundColor Green
}
else {
    Write-Host "[FAIL] Rapports Evidently" -ForegroundColor Red
}

if ($success2) {
    Write-Host "[OK] Alertes Qualite: Quotidien a 08h00" -ForegroundColor Green
}
else {
    Write-Host "[FAIL] Alertes Qualite" -ForegroundColor Red
}

if ($success3) {
    Write-Host "[OK] Backup DVC: Quotidien a 02h00" -ForegroundColor Green
}
else {
    Write-Host "[FAIL] Backup DVC" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  COMMANDES UTILES" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Lister les taches:" -ForegroundColor Yellow
Write-Host "Get-ScheduledTask | Where-Object {`$_.TaskName -like 'Chatbot-*'}" -ForegroundColor Gray
Write-Host ""
Write-Host "# Executer une tache manuellement:" -ForegroundColor Yellow
Write-Host "Start-ScheduledTask -TaskName 'Chatbot-Evidently-Reports'" -ForegroundColor Gray
Write-Host ""
Write-Host "# Desactiver une tache:" -ForegroundColor Yellow
Write-Host "Disable-ScheduledTask -TaskName 'Chatbot-Evidently-Reports'" -ForegroundColor Gray
Write-Host ""
Write-Host "# Supprimer toutes les taches:" -ForegroundColor Yellow
Write-Host ".\scripts\setup_scheduled_tasks.ps1 -Remove" -ForegroundColor Gray
Write-Host ""
Write-Host "[OK] Configuration terminee!" -ForegroundColor Green
