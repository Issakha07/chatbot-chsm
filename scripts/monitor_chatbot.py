"""
Monitoring de la qualité du chatbot avec Evidently
Surveille les questions, réponses et détecte les drifts
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TextOverviewPreset
from evidently.metrics import *

sys.path.insert(0, str(Path(__file__).parent.parent))

class ChatbotMonitor:
    """Monitoring du chatbot avec Evidently"""
    
    def __init__(self, logs_dir: str = "./logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir = Path("./reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def load_conversations(self, days: int = 7) -> pd.DataFrame:
        """Charger les conversations des N derniers jours"""
        # Pour l'instant, retourne des données de test
        # À remplacer par votre vrai système de logs
        
        # Exemple de données
        data = {
            "timestamp": [
                "2024-11-20 10:30:00", "2024-11-20 11:15:00",
                "2024-11-21 09:00:00", "2024-11-21 14:30:00",
                "2024-11-22 08:45:00"
            ],
            "question": [
                "Comment réinitialiser mon mot de passe?",
                "Procédure pour demander un nouveau PC",
                "Créer un ticket de support",
                "Accès VPN à distance",
                "Installation imprimante réseau"
            ],
            "answer": [
                "Pour réinitialiser votre mot de passe...",
                "La procédure de demande de matériel...",
                "Vous pouvez créer un ticket via...",
                "L'accès VPN nécessite...",
                "L'installation d'imprimante se fait..."
            ],
            "response_time": [1.2, 1.5, 0.9, 1.8, 1.1],
            "has_answer": [True, True, True, True, True],
            "confidence": [0.92, 0.87, 0.95, 0.83, 0.89]
        }
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def split_reference_current(self, df: pd.DataFrame, split_date: str = None):
        """Séparer les données de référence et actuelles"""
        if split_date is None:
            # Par défaut, 70% référence, 30% actuel
            split_idx = int(len(df) * 0.7)
            reference = df.iloc[:split_idx]
            current = df.iloc[split_idx:]
        else:
            split_datetime = pd.to_datetime(split_date)
            reference = df[df['timestamp'] < split_datetime]
            current = df[df['timestamp'] >= split_datetime]
        
        return reference, current
    
    def generate_data_drift_report(self, reference: pd.DataFrame, current: pd.DataFrame):
        """Générer rapport de drift des données"""
        
        column_mapping = ColumnMapping(
            text_features=["question", "answer"],
            numerical_features=["response_time", "confidence"]
        )
        
        report = Report(metrics=[
            DataDriftPreset(),
            TextOverviewPreset(column_name="question"),
            ColumnDriftMetric(column_name="response_time"),
            ColumnDriftMetric(column_name="confidence"),
        ])
        
        report.run(
            reference_data=reference,
            current_data=current,
            column_mapping=column_mapping
        )
        
        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"drift_report_{timestamp}.html"
        report.save_html(str(report_path))
        
        print(f"✅ Rapport de drift sauvegardé: {report_path}")
        return report_path
    
    def generate_performance_report(self, df: pd.DataFrame):
        """Générer rapport de performance"""
        
        # Calculer métriques
        metrics = {
            "total_questions": len(df),
            "avg_response_time": df["response_time"].mean(),
            "avg_confidence": df["confidence"].mean(),
            "success_rate": (df["has_answer"].sum() / len(df)) * 100,
            "questions_per_day": df.groupby(df['timestamp'].dt.date).size().mean()
        }
        
        report = Report(metrics=[
            ColumnSummaryMetric(column_name="response_time"),
            ColumnSummaryMetric(column_name="confidence"),
            ColumnDistributionMetric(column_name="response_time"),
        ])
        
        report.run(current_data=df, reference_data=None)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"performance_report_{timestamp}.html"
        report.save_html(str(report_path))
        
        print(f"✅ Rapport de performance sauvegardé: {report_path}")
        
        # Sauvegarder métriques JSON
        metrics_path = self.reports_dir / f"metrics_{timestamp}.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"""
📊 Métriques de Performance:
   - Questions totales: {metrics['total_questions']}
   - Temps réponse moyen: {metrics['avg_response_time']:.2f}s
   - Confiance moyenne: {metrics['avg_confidence']:.2%}
   - Taux de succès: {metrics['success_rate']:.1f}%
   - Questions/jour: {metrics['questions_per_day']:.1f}
        """)
        
        return report_path, metrics
    
    def detect_new_topics(self, reference: pd.DataFrame, current: pd.DataFrame):
        """Détecter les nouveaux sujets de questions"""
        
        # Mots-clés dans les questions de référence
        ref_words = set()
        for question in reference['question']:
            ref_words.update(question.lower().split())
        
        # Nouveaux mots dans les questions actuelles
        new_topics = []
        for question in current['question']:
            words = set(question.lower().split())
            new_words = words - ref_words
            if new_words:
                new_topics.append({
                    "question": question,
                    "new_words": list(new_words)
                })
        
        if new_topics:
            print(f"⚠️  {len(new_topics)} nouvelles questions détectées")
            print("💡 Suggéré: Ajouter de nouveaux documents couvrant ces sujets")
        
        return new_topics
    
    def run_full_monitoring(self):
        """Lancer le monitoring complet"""
        print("🔍 Démarrage du monitoring...")
        
        # Charger les données
        df = self.load_conversations()
        print(f"📊 {len(df)} conversations chargées")
        
        # Séparer référence/actuel
        reference, current = self.split_reference_current(df)
        print(f"📅 Référence: {len(reference)}, Actuel: {len(current)}")
        
        # Générer rapports
        drift_report = self.generate_data_drift_report(reference, current)
        perf_report, metrics = self.generate_performance_report(df)
        
        # Détecter nouveaux sujets
        new_topics = self.detect_new_topics(reference, current)
        
        print(f"""
✅ Monitoring terminé!
   - Rapport drift: {drift_report}
   - Rapport performance: {perf_report}
   - Nouveaux sujets: {len(new_topics)}
        """)
        
        return {
            "drift_report": str(drift_report),
            "performance_report": str(perf_report),
            "metrics": metrics,
            "new_topics": new_topics
        }


def main():
    """Point d'entrée du script"""
    monitor = ChatbotMonitor()
    monitor.run_full_monitoring()


if __name__ == "__main__":
    main()
