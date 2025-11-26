# ⚙️ Automatisation des Rapports Evidently

## 🎯 Options d'Automatisation

### Option 1 : Planificateur de Tâches Windows (Recommandé)

#### Configuration Manuelle

1. **Ouvrir le Planificateur de Tâches**
   - Appuyez sur `Win + R`
   - Tapez `taskschd.msc`
   - Appuyez sur Entrée

2. **Créer une Nouvelle Tâche**
   - Cliquez sur "Créer une tâche..." (panneau de droite)
   - Nom : `Chatbot Evidently Reports`
   - Description : `Génération automatique des rapports de monitoring`
   - Cochez "Exécuter même si l'utilisateur n'est pas connecté"

3. **Configurer le Déclencheur**
   - Onglet "Déclencheurs" → "Nouveau..."
   - **Quotidien** : Tous les jours à 23:00
   - Ou **Hebdomadaire** : Tous les lundis à 09:00

4. **Configurer l'Action**
   - Onglet "Actions" → "Nouveau..."
   - Action : `Démarrer un programme`
   - Programme : `powershell.exe`
   - Arguments : `-ExecutionPolicy Bypass -File "J:\Stage-Hopital\stage\chatbot-chsm\scripts\automate_reports.ps1"`
   - Répertoire : `J:\Stage-Hopital\stage\chatbot-chsm`

5. **Paramètres Avancés**
   - Onglet "Conditions"
     - ☑ Démarrer uniquement si l'ordinateur est relié au secteur
     - ☐ Arrêter si l'ordinateur fonctionne sur batterie
   - Onglet "Paramètres"
     - ☑ Autoriser l'exécution de la tâche à la demande
     - ☑ Si la tâche échoue, recommencer tous les : `10 minutes`

---

#### Configuration via PowerShell

```powershell
# Créer la tâche planifiée automatiquement
$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"J:\Stage-Hopital\stage\chatbot-chsm\scripts\automate_reports.ps1`"" `
    -WorkingDirectory "J:\Stage-Hopital\stage\chatbot-chsm"

$Trigger = New-ScheduledTaskTrigger -Daily -At "23:00"

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "Chatbot Evidently Reports" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Génération automatique des rapports de monitoring Evidently"
```

**Tester la tâche :**
```powershell
Start-ScheduledTask -TaskName "Chatbot Evidently Reports"
```

**Désactiver la tâche :**
```powershell
Disable-ScheduledTask -TaskName "Chatbot Evidently Reports"
```

**Supprimer la tâche :**
```powershell
Unregister-ScheduledTask -TaskName "Chatbot Evidently Reports" -Confirm:$false
```

---

### Option 2 : Script Python avec APScheduler

#### Installation
```powershell
pip install apscheduler
```

#### Script Python (`scripts/scheduler.py`)

```python
"""
Scheduler pour automatiser la génération de rapports Evidently
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_report():
    """Générer un rapport Evidently"""
    logger.info("🚀 Démarrage de la génération du rapport...")
    
    try:
        # Exécuter le script de monitoring
        result = subprocess.run(
            ["python", "scripts/monitor_chatbot.py"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("✅ Rapport généré avec succès")
        logger.info(result.stdout)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors de la génération du rapport: {e}")
        logger.error(e.stderr)

def cleanup_old_reports(keep_last=30):
    """Nettoyer les anciens rapports"""
    logger.info("🧹 Nettoyage des anciens rapports...")
    
    reports_dir = Path("reports")
    reports = sorted(
        reports_dir.glob("chatbot_monitoring_*.html"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    for old_report in reports[keep_last:]:
        old_report.unlink()
        logger.info(f"🗑️  Supprimé: {old_report.name}")

def scheduled_job():
    """Tâche planifiée complète"""
    logger.info("=" * 60)
    logger.info(f"📊 Exécution planifiée - {datetime.now()}")
    logger.info("=" * 60)
    
    generate_report()
    cleanup_old_reports()
    
    logger.info("✨ Tâche terminée")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Planifier la génération quotidienne à 23:00
    scheduler.add_job(
        scheduled_job,
        CronTrigger(hour=23, minute=0),
        id='daily_report',
        name='Génération rapport quotidien'
    )
    
    # Planifier le nettoyage hebdomadaire (dimanche 02:00)
    scheduler.add_job(
        cleanup_old_reports,
        CronTrigger(day_of_week='sun', hour=2, minute=0),
        id='weekly_cleanup',
        name='Nettoyage hebdomadaire'
    )
    
    logger.info("🤖 Scheduler démarré - Rapports quotidiens à 23:00")
    logger.info("📋 Tâches planifiées:")
    scheduler.print_jobs()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Scheduler arrêté")
```

**Exécuter le scheduler :**
```powershell
python scripts/scheduler.py
```

**Exécuter en arrière-plan (Windows) :**
```powershell
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "scripts/scheduler.py"
```

---

### Option 3 : Conteneur Docker avec Cron

#### Dockerfile pour le scheduler

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Installer cron
RUN apt-get update && apt-get install -y cron

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configurer cron
COPY scripts/crontab /etc/cron.d/evidently-cron
RUN chmod 0644 /etc/cron.d/evidently-cron
RUN crontab /etc/cron.d/evidently-cron

# Démarrer cron
CMD ["cron", "-f"]
```

#### Fichier crontab (`scripts/crontab`)

```cron
# Génération quotidienne à 23:00
0 23 * * * cd /app && python scripts/monitor_chatbot.py >> /var/log/cron.log 2>&1

# Nettoyage hebdomadaire (dimanche 02:00)
0 2 * * 0 cd /app && find reports/ -name "*.html" -mtime +30 -delete >> /var/log/cron.log 2>&1
```

---

## 📊 Monitoring de l'Automatisation

### Vérifier les logs

```powershell
# Logs du script PowerShell
Get-Content J:\Stage-Hopital\stage\chatbot-chsm\automation.log -Tail 50

# Logs du scheduler Python
Get-Content J:\Stage-Hopital\stage\chatbot-chsm\scheduler.log -Tail 50

# Logs du Planificateur de Tâches Windows
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20 | 
    Where-Object { $_.Message -like "*Chatbot*" }
```

### Dashboard de surveillance

Créer un script de vérification :

```powershell
# scripts/check_automation.ps1

$ReportsDir = "reports"
$LatestReport = Get-ChildItem -Path $ReportsDir -Filter "*.html" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

if ($LatestReport) {
    $Age = (Get-Date) - $LatestReport.LastWriteTime
    
    if ($Age.TotalHours -gt 25) {
        Write-Warning "⚠️  Aucun rapport généré depuis plus de 25 heures!"
        # Envoyer une alerte
    } else {
        Write-Host "✅ Dernier rapport: $($LatestReport.Name) (il y a $([math]::Round($Age.TotalHours, 1))h)"
    }
} else {
    Write-Warning "❌ Aucun rapport trouvé!"
}
```

---

## 📧 Notifications par Email (Optionnel)

### Configuration SMTP dans PowerShell

```powershell
# Configuration
$EmailParams = @{
    From = "chatbot@hopital.fr"
    To = "admin@hopital.fr"
    Subject = "Rapport Evidently - $(Get-Date -Format 'dd/MM/yyyy')"
    Body = "Veuillez trouver en pièce jointe le rapport de monitoring du chatbot."
    SmtpServer = "smtp.hopital.fr"
    Port = 587
    UseSsl = $true
    Credential = Get-Credential
    Attachments = $LatestReport.FullName
}

Send-MailMessage @EmailParams
```

### Alternative : SendGrid API

```python
# Installation: pip install sendgrid

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
import base64

def send_report_email(report_path):
    message = Mail(
        from_email='chatbot@hopital.fr',
        to_emails='admin@hopital.fr',
        subject='Rapport Evidently Chatbot',
        html_content='<p>Rapport de monitoring en pièce jointe</p>'
    )
    
    # Ajouter le fichier
    with open(report_path, 'rb') as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    
    attachment = Attachment()
    attachment.file_content = encoded
    attachment.file_name = 'rapport_evidently.html'
    attachment.file_type = 'text/html'
    message.attachment = attachment
    
    sg = SendGridAPIClient(api_key='YOUR_SENDGRID_API_KEY')
    response = sg.send(message)
```

---

## 🎯 Exemples de Planification

| Fréquence | Cron Expression | Description |
|-----------|----------------|-------------|
| Toutes les heures | `0 * * * *` | À chaque heure pile |
| Quotidien (23h) | `0 23 * * *` | Chaque jour à 23:00 |
| Hebdomadaire (Lundi 9h) | `0 9 * * 1` | Tous les lundis à 09:00 |
| Mensuel (1er du mois) | `0 0 1 * *` | Le 1er de chaque mois à minuit |
| Toutes les 6h | `0 */6 * * *` | À 00:00, 06:00, 12:00, 18:00 |

---

## 🚨 Troubleshooting

### Le script ne s'exécute pas

1. Vérifier les permissions :
   ```powershell
   Get-ExecutionPolicy
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

2. Vérifier les chemins absolus dans la tâche planifiée

3. Tester manuellement :
   ```powershell
   powershell -ExecutionPolicy Bypass -File "scripts/automate_reports.ps1"
   ```

### Erreurs Python

- Vérifier que l'environnement virtuel est activé
- Vérifier les dépendances : `pip list | findstr evidently`

---

## 📖 Ressources

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Windows Task Scheduler](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [Cron Expression Generator](https://crontab.guru/)
