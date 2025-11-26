# Guide Evidently - Monitoring du Chatbot

## 🎯 Objectif

Surveiller la qualité et la performance de votre chatbot en temps réel.

## 📊 Ce qu'Evidently Surveille

### 1. **Data Drift** (Dérive des données)
- Les questions posées changent-elles au fil du temps ?
- Les nouveaux utilisateurs posent-ils des questions différentes ?

### 2. **Performance**
- Temps de réponse moyen
- Taux de questions sans réponse
- Confiance du modèle

### 3. **Text Analytics**
- Mots-clés les plus fréquents
- Longueur des questions/réponses
- Sentiment des utilisateurs

## 🔧 Configuration

### Installation

```powershell
pip install evidently
```

### Structure des Logs

Créez un système de logging dans votre backend :

```python
# backend/app.py
import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def log_conversation(question: str, answer: str, response_time: float, confidence: float):
    """Logger une conversation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "response_time": response_time,
        "confidence": confidence,
        "has_answer": len(answer) > 0
    }
    
    # Ajouter au fichier du jour
    log_file = LOG_DIR / f"chat_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
```

### Intégrer dans l'endpoint Chat

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    start_time = time.time()
    
    # Générer réponse
    response = rag_system.chat(request.message, request.language)
    
    # Calculer temps
    response_time = time.time() - start_time
    
    # Logger
    log_conversation(
        question=request.message,
        answer=response,
        response_time=response_time,
        confidence=0.85  # À calculer réellement
    )
    
    return {"response": response}
```

## 📈 Génération de Rapports

### Rapport Journalier Automatique

Créez un script `scripts/daily_report.py` :

```python
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import json

def generate_daily_report():
    """Générer rapport des dernières 24h"""
    
    # Charger logs du jour
    log_file = Path(f"logs/chat_{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    if not log_file.exists():
        print("Pas de données aujourd'hui")
        return
    
    # Lire les logs
    conversations = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            conversations.append(json.loads(line))
    
    df = pd.DataFrame(conversations)
    
    # Calculer métriques
    print(f"""
📊 Rapport Journalier - {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Volume
   • Questions totales: {len(df)}
   • Questions/heure: {len(df) / 24:.1f}

⏱️  Performance
   • Temps réponse moyen: {df['response_time'].mean():.2f}s
   • Temps réponse max: {df['response_time'].max():.2f}s
   • Temps réponse min: {df['response_time'].min():.2f}s

✅ Qualité
   • Taux de réponse: {(df['has_answer'].sum() / len(df)) * 100:.1f}%
   • Confiance moyenne: {df['confidence'].mean():.2%}

🔥 Top 5 Questions
    """)
    
    # Top questions
    for i, q in enumerate(df['question'].value_counts().head(5).items(), 1):
        print(f"   {i}. {q[0]} ({q[1]}x)")
    
    # Alertes
    if df['response_time'].mean() > 2.0:
        print("\n⚠️  ALERTE: Temps de réponse élevé (>2s)")
    
    if (df['has_answer'].sum() / len(df)) < 0.8:
        print("\n⚠️  ALERTE: Taux de réponse faible (<80%)")

if __name__ == "__main__":
    generate_daily_report()
```

### Rapport Hebdomadaire avec Drift

```python
# scripts/weekly_drift_report.py
from monitor_chatbot import ChatbotMonitor

def weekly_report():
    monitor = ChatbotMonitor()
    
    # Charger 14 derniers jours
    df = monitor.load_conversations(days=14)
    
    # Semaine dernière vs cette semaine
    reference = df[df['timestamp'] < (datetime.now() - timedelta(days=7))]
    current = df[df['timestamp'] >= (datetime.now() - timedelta(days=7))]
    
    # Générer rapport
    monitor.generate_data_drift_report(reference, current)
    
    print("""
📧 Rapport hebdomadaire envoyé!
   - Consultez reports/drift_report_*.html
    """)

if __name__ == "__main__":
    weekly_report()
```

## 🤖 Automatisation

### Cron Job (Linux/Mac)

```bash
# Rapport journalier à 23h
0 23 * * * cd /path/to/chatbot && ./venv/bin/python scripts/daily_report.py

# Rapport hebdomadaire le dimanche à 18h
0 18 * * 0 cd /path/to/chatbot && ./venv/bin/python scripts/weekly_drift_report.py
```

### Task Scheduler (Windows)

```powershell
# Créer tâche planifiée quotidienne
$action = New-ScheduledTaskAction -Execute 'python' -Argument 'scripts\daily_report.py' -WorkingDirectory 'J:\Stage-Hopital\stage\chatbot-chsm'
$trigger = New-ScheduledTaskTrigger -Daily -At 23:00
Register-ScheduledTask -TaskName "Chatbot Daily Report" -Action $action -Trigger $trigger
```

## 📊 Dashboard Streamlit

Intégrez Evidently dans votre interface Streamlit :

```python
# Dans interface-streamlit.py
import streamlit as st
from pathlib import Path

# Sidebar
with st.sidebar:
    if st.button("📊 Voir Rapports"):
        st.switch_page("pages/reports.py")

# pages/reports.py
import streamlit as st
from pathlib import Path

st.title("📊 Rapports de Monitoring")

# Lister les rapports
reports = list(Path("reports").glob("*.html"))

if reports:
    selected = st.selectbox("Choisir un rapport", reports)
    
    # Afficher le rapport HTML
    with open(selected, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=800, scrolling=True)
else:
    st.info("Aucun rapport disponible. Lancez `python scripts/monitor_chatbot.py`")
```

## 🎯 Métriques Clés à Surveiller

### 1. **Data Drift Score**
- < 0.3 : Stable ✅
- 0.3 - 0.5 : Surveillance 👀
- > 0.5 : Action requise ⚠️

### 2. **Temps de Réponse**
- < 1s : Excellent ✅
- 1-2s : Bon 👍
- > 2s : À optimiser ⚠️

### 3. **Taux de "Je ne sais pas"**
- < 5% : Excellent ✅
- 5-10% : Acceptable 👍
- > 10% : Ajouter documents ⚠️

## 🚨 Alertes Automatiques

Créez `scripts/check_alerts.py` :

```python
def check_alerts():
    """Vérifier les seuils et alerter"""
    df = load_today_logs()
    
    alerts = []
    
    # Alerte temps de réponse
    if df['response_time'].mean() > 2.0:
        alerts.append("⚠️  Temps de réponse élevé")
    
    # Alerte taux de réponse
    answer_rate = (df['has_answer'].sum() / len(df))
    if answer_rate < 0.8:
        alerts.append(f"⚠️  Taux de réponse faible: {answer_rate:.1%}")
    
    # Alerte volume
    if len(df) > 1000:
        alerts.append("📈 Volume élevé: pic de demandes")
    
    if alerts:
        send_email_alert(alerts)  # À implémenter
        print("\n".join(alerts))

if __name__ == "__main__":
    check_alerts()
```

## 📧 Notifications

Intégrez avec votre système de notifications :

```python
# Slack
import requests

def send_slack_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={"text": message})

# Email
import smtplib
from email.mime.text import MIMEText

def send_email_alert(alerts):
    msg = MIMEText("\n".join(alerts))
    msg['Subject'] = '🚨 Alerte Chatbot CHSM'
    msg['From'] = 'chatbot@chsm.com'
    msg['To'] = 'admin@chsm.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your_email', 'your_password')
        server.send_message(msg)
```
