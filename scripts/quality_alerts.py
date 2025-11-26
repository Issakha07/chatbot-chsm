"""
Systeme d'alertes pour la qualite du chatbot
Detecte les degradations et envoie des notifications
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class QualityAlerts:
    """Systeme d'alertes pour la qualite du chatbot"""
    
    def __init__(self, logs_dir: str = "./logs"):
        self.logs_dir = Path(logs_dir)
        self.alerts_log = Path("quality_alerts.log")
        
        # Seuils d'alerte
        self.thresholds = {
            'min_confidence': 0.70,          # Confiance minimale acceptable
            'max_response_time': 3.0,        # Temps de reponse max (secondes)
            'min_daily_conversations': 5,    # Conversations mini par jour
            'error_rate_threshold': 0.15,    # Taux d'erreur max (15%)
        }
    
    def load_recent_conversations(self, days: int = 1) -> pd.DataFrame:
        """Charger les conversations recentes"""
        conversations = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        log_files = sorted(self.logs_dir.glob("chat_*.jsonl"))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            conv = json.loads(line)
                            # Convertir timestamp en datetime
                            try:
                                conv_date = datetime.fromisoformat(conv['timestamp'])
                                if conv_date >= cutoff_date:
                                    conversations.append(conv)
                            except:
                                # Ajouter quand meme si pas de timestamp
                                conversations.append(conv)
            except Exception as e:
                logger.error(f"Erreur lecture {log_file.name}: {e}")
        
        if not conversations:
            return pd.DataFrame()
        
        return pd.DataFrame(conversations)
    
    def check_confidence(self, df: pd.DataFrame) -> Dict:
        """Verifier le niveau de confiance"""
        if df.empty or 'confidence' not in df:
            return {'status': 'unknown', 'message': 'Aucune donnee de confiance'}
        
        avg_confidence = df['confidence'].mean()
        min_confidence = df['confidence'].min()
        low_confidence_count = len(df[df['confidence'] < self.thresholds['min_confidence']])
        low_confidence_rate = low_confidence_count / len(df)
        
        alert = {
            'metric': 'confidence',
            'avg_value': avg_confidence,
            'min_value': min_confidence,
            'low_count': low_confidence_count,
            'low_rate': low_confidence_rate,
            'threshold': self.thresholds['min_confidence'],
            'status': 'ok',
            'message': f"Confiance moyenne: {avg_confidence:.1%}"
        }
        
        if avg_confidence < self.thresholds['min_confidence']:
            alert['status'] = 'critical'
            alert['message'] = f"CRITIQUE: Confiance moyenne ({avg_confidence:.1%}) sous le seuil ({self.thresholds['min_confidence']:.1%})"
        elif low_confidence_rate > 0.3:  # Plus de 30% de reponses a faible confiance
            alert['status'] = 'warning'
            alert['message'] = f"ATTENTION: {low_confidence_rate:.1%} des reponses ont une confiance faible"
        
        return alert
    
    def check_response_time(self, df: pd.DataFrame) -> Dict:
        """Verifier les temps de reponse"""
        if df.empty or 'response_time' not in df:
            return {'status': 'unknown', 'message': 'Aucune donnee de temps de reponse'}
        
        avg_time = df['response_time'].mean()
        max_time = df['response_time'].max()
        slow_count = len(df[df['response_time'] > self.thresholds['max_response_time']])
        slow_rate = slow_count / len(df)
        
        alert = {
            'metric': 'response_time',
            'avg_value': avg_time,
            'max_value': max_time,
            'slow_count': slow_count,
            'slow_rate': slow_rate,
            'threshold': self.thresholds['max_response_time'],
            'status': 'ok',
            'message': f"Temps moyen: {avg_time:.2f}s"
        }
        
        if avg_time > self.thresholds['max_response_time']:
            alert['status'] = 'critical'
            alert['message'] = f"CRITIQUE: Temps moyen ({avg_time:.2f}s) au-dessus du seuil ({self.thresholds['max_response_time']}s)"
        elif slow_rate > 0.2:  # Plus de 20% de reponses lentes
            alert['status'] = 'warning'
            alert['message'] = f"ATTENTION: {slow_rate:.1%} des reponses sont lentes"
        
        return alert
    
    def check_volume(self, df: pd.DataFrame) -> Dict:
        """Verifier le volume de conversations"""
        if df.empty:
            return {
                'metric': 'volume',
                'value': 0,
                'threshold': self.thresholds['min_daily_conversations'],
                'status': 'critical',
                'message': f"CRITIQUE: Aucune conversation detectee"
            }
        
        conv_count = len(df)
        
        alert = {
            'metric': 'volume',
            'value': conv_count,
            'threshold': self.thresholds['min_daily_conversations'],
            'status': 'ok',
            'message': f"Volume: {conv_count} conversations"
        }
        
        if conv_count < self.thresholds['min_daily_conversations']:
            alert['status'] = 'warning'
            alert['message'] = f"ATTENTION: Volume faible ({conv_count} conversations, minimum: {self.thresholds['min_daily_conversations']})"
        
        return alert
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """Detecter des anomalies dans les donnees"""
        anomalies = []
        
        if df.empty:
            return anomalies
        
        # Detecter questions tres courtes (possibles erreurs)
        if 'question' in df.columns:
            df['question_length'] = df['question'].str.len()
            very_short = df[df['question_length'] < 5]
            if len(very_short) > 0:
                anomalies.append({
                    'type': 'very_short_questions',
                    'count': len(very_short),
                    'message': f"{len(very_short)} question(s) tres courte(s) detectee(s)"
                })
        
        # Detecter reponses identiques repetees (possible bug)
        if 'answer' in df.columns:
            duplicate_answers = df['answer'].value_counts()
            high_duplicates = duplicate_answers[duplicate_answers > len(df) * 0.5]
            if len(high_duplicates) > 0:
                anomalies.append({
                    'type': 'duplicate_answers',
                    'count': len(high_duplicates),
                    'message': f"Reponse(s) identique(s) repetee(s) plus de 50% du temps"
                })
        
        return anomalies
    
    def generate_alert_report(self, days: int = 1) -> Dict:
        """Generer un rapport complet d'alertes"""
        logger.info(f"Analyse qualite sur les {days} dernier(s) jour(s)...")
        
        df = self.load_recent_conversations(days=days)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'total_conversations': len(df),
            'alerts': [],
            'anomalies': [],
            'overall_status': 'ok'
        }
        
        # Verifications
        alerts = [
            self.check_confidence(df),
            self.check_response_time(df),
            self.check_volume(df)
        ]
        
        report['alerts'] = alerts
        report['anomalies'] = self.detect_anomalies(df)
        
        # Determiner statut global
        if any(a['status'] == 'critical' for a in alerts):
            report['overall_status'] = 'critical'
        elif any(a['status'] == 'warning' for a in alerts):
            report['overall_status'] = 'warning'
        
        return report
    
    def log_alert(self, alert: Dict):
        """Enregistrer une alerte dans le fichier log"""
        with open(self.alerts_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert, ensure_ascii=False) + '\n')
    
    def print_report(self, report: Dict):
        """Afficher le rapport d'alertes"""
        print("\n" + "="*60)
        print(f"  RAPPORT D'ALERTES QUALITE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # Statut global
        status_symbols = {
            'ok': '[OK]',
            'warning': '[ATTENTION]',
            'critical': '[CRITIQUE]',
            'unknown': '[?]'
        }
        
        print(f"\nStatut global: {status_symbols[report['overall_status']]} {report['overall_status'].upper()}")
        print(f"Periode: {report['period_days']} jour(s)")
        print(f"Total conversations: {report['total_conversations']}")
        
        # Alertes
        print("\n--- ALERTES ---")
        for alert in report['alerts']:
            symbol = status_symbols.get(alert['status'], '[?]')
            print(f"{symbol} {alert['message']}")
        
        # Anomalies
        if report['anomalies']:
            print("\n--- ANOMALIES DETECTEES ---")
            for anomaly in report['anomalies']:
                print(f"[!] {anomaly['message']}")
        else:
            print("\n[OK] Aucune anomalie detectee")
        
        print("\n" + "="*60 + "\n")
    
    def send_notification(self, report: Dict):
        """Envoyer une notification (a implementer)"""
        # TODO: Implementer envoi email, Slack, Teams, etc.
        if report['overall_status'] in ['critical', 'warning']:
            logger.warning(f"ALERTE: {report['overall_status'].upper()} - Notification a implementer")


def main():
    """Point d'entree principal"""
    alerts = QualityAlerts(logs_dir="./logs")
    
    # Generer rapport sur les dernieres 24h
    report = alerts.generate_alert_report(days=1)
    
    # Afficher le rapport
    alerts.print_report(report)
    
    # Enregistrer l'alerte
    alerts.log_alert(report)
    
    # Envoyer notification si necessaire
    alerts.send_notification(report)
    
    # Code de sortie selon statut
    if report['overall_status'] == 'critical':
        sys.exit(2)  # Code erreur critique
    elif report['overall_status'] == 'warning':
        sys.exit(1)  # Code erreur warning
    else:
        sys.exit(0)  # OK


if __name__ == "__main__":
    main()
