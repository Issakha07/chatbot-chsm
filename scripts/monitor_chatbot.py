"""
Monitoring de la qualité du chatbot avec Evidently
Surveille les questions, réponses et détecte les drifts
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class ChatbotMonitor:
    """Monitoring du chatbot avec Evidently"""
    
    def __init__(self, logs_dir: str = "./logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir = Path("./reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def load_conversations(self, days: int = 7) -> pd.DataFrame:
        """Charger les conversations des fichiers JSONL"""
        conversations = []
        
        # Lister tous les fichiers de logs
        log_files = sorted(self.logs_dir.glob("chat_*.jsonl"))
        
        if not log_files:
            logger.warning("⚠️  Aucun fichier de logs trouvé")
            return pd.DataFrame()
        
        logger.info(f"📂 Chargement de {len(log_files)} fichier(s) de logs...")
        
        # Charger chaque fichier JSONL
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            conv = json.loads(line)
                            conversations.append(conv)
            except Exception as e:
                logger.error(f"❌ Erreur lecture {log_file.name}: {e}")
        
        if not conversations:
            logger.warning("⚠️  Aucune conversation trouvée dans les logs")
            return pd.DataFrame()
        
        df = pd.DataFrame(conversations)
        logger.info(f"✅ {len(df)} conversations chargées")
        
        return df
    
    def generate_basic_stats(self, df: pd.DataFrame) -> dict:
        """Générer des statistiques basiques"""
        if df.empty:
            return {}
        
        stats = {
            'total_conversations': len(df),
            'avg_response_time': df['response_time'].mean() if 'response_time' in df else 0,
            'avg_confidence': df['confidence'].mean() if 'confidence' in df else 0,
            'languages': df['language'].value_counts().to_dict() if 'language' in df else {},
            'date_range': {
                'start': df['timestamp'].min() if 'timestamp' in df else None,
                'end': df['timestamp'].max() if 'timestamp' in df else None
            }
        }
        
        return stats
    
    def analyze_questions(self, df: pd.DataFrame) -> dict:
        """Analyser les types de questions posées"""
        if df.empty or 'question' not in df:
            return {}
        
        # Longueur moyenne des questions
        df['question_length'] = df['question'].str.len()
        
        # Mots-clés fréquents (simple extraction)
        all_words = ' '.join(df['question'].tolist()).lower()
        keywords = {}
        
        # Mots-clés IT communs
        it_keywords = [
            'mot de passe', 'password', 'vpn', 'connexion', 'accès',
            'logiciel', 'application', 'service', 'support', 'problème',
            'erreur', 'installation', 'configuration', 'email', 'réseau'
        ]
        
        for keyword in it_keywords:
            count = all_words.count(keyword.lower())
            if count > 0:
                keywords[keyword] = count
        
        analysis = {
            'total_questions': len(df),
            'avg_question_length': df['question_length'].mean(),
            'min_question_length': df['question_length'].min(),
            'max_question_length': df['question_length'].max(),
            'top_keywords': dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10])
        }
        
        return analysis
    
    def generate_html_report(self, df: pd.DataFrame) -> str:
        """Générer un rapport HTML personnalisé"""
        stats = self.generate_basic_stats(df)
        questions_analysis = self.analyze_questions(df)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"chatbot_monitoring_{timestamp}.html"
        
        # Template HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Monitoring Chatbot - {datetime.now().strftime("%Y-%m-%d %H:%M")}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card.green {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric-card.orange {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .metric-card.blue {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 30px;
            text-align: center;
        }}
        .alert {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport de Monitoring Chatbot IT Support</h1>
        <p class="timestamp">Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
        
        <div class="success">
            <strong>✅ Statut :</strong> Système opérationnel - {stats.get('total_conversations', 0)} conversations analysées
        </div>
        
        <h2>📈 Métriques Principales</h2>
        <div class="metric-grid">
            <div class="metric-card blue">
                <div class="metric-label">Total Conversations</div>
                <div class="metric-value">{stats.get('total_conversations', 0)}</div>
            </div>
            
            <div class="metric-card green">
                <div class="metric-label">Temps de Réponse Moyen</div>
                <div class="metric-value">{stats.get('avg_response_time', 0):.2f}s</div>
            </div>
            
            <div class="metric-card orange">
                <div class="metric-label">Confiance Moyenne</div>
                <div class="metric-value">{stats.get('avg_confidence', 0):.1%}</div>
            </div>
        </div>
        
        <h2>💬 Analyse des Questions</h2>
        <table>
            <tr>
                <th>Métrique</th>
                <th>Valeur</th>
            </tr>
            <tr>
                <td>Nombre de questions</td>
                <td>{questions_analysis.get('total_questions', 0)}</td>
            </tr>
            <tr>
                <td>Longueur moyenne</td>
                <td>{questions_analysis.get('avg_question_length', 0):.0f} caractères</td>
            </tr>
            <tr>
                <td>Question la plus courte</td>
                <td>{questions_analysis.get('min_question_length', 0)} caractères</td>
            </tr>
            <tr>
                <td>Question la plus longue</td>
                <td>{questions_analysis.get('max_question_length', 0)} caractères</td>
            </tr>
        </table>
        
        <h2>🔑 Mots-clés les Plus Fréquents</h2>
        <table>
            <tr>
                <th>Mot-clé</th>
                <th>Occurrences</th>
            </tr>
"""
        
        # Ajouter les mots-clés
        for keyword, count in questions_analysis.get('top_keywords', {}).items():
            html_content += f"""
            <tr>
                <td>{keyword}</td>
                <td>{count}</td>
            </tr>
"""
        
        html_content += """
        </table>
        
        <h2>📋 Dernières Conversations</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Question</th>
                <th>Temps (s)</th>
                <th>Confiance</th>
            </tr>
"""
        
        # Ajouter les dernières conversations
        for _, row in df.tail(10).iterrows():
            html_content += f"""
            <tr>
                <td>{row.get('timestamp', 'N/A')}</td>
                <td>{row.get('question', 'N/A')[:100]}...</td>
                <td>{row.get('response_time', 0):.2f}</td>
                <td>{row.get('confidence', 0):.1%}</td>
            </tr>
"""
        
        html_content += """
        </table>
        
        <div class="alert">
            <strong>ℹ️ Note :</strong> Ce rapport est généré automatiquement. Pour une analyse plus approfondie avec détection de drift, 
            assurez-vous d'avoir au moins 2 périodes de données distinctes.
        </div>
        
        <p class="timestamp">
            Généré par Evidently AI Monitoring System<br>
            Chatbot CHSM - IT Support
        </p>
    </div>
</body>
</html>
"""
        
        # Sauvegarder le rapport
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Rapport HTML sauvegardé : {report_path}")
        return str(report_path)


def main():
    """Point d'entrée principal"""
    logger.info("🚀 Démarrage du monitoring Evidently...")
    
    monitor = ChatbotMonitor(logs_dir="./logs")
    
    # Charger les conversations
    df = monitor.load_conversations(days=30)
    
    if df.empty:
        logger.error("❌ Aucune donnée à analyser. Assurez-vous que des conversations sont loggées.")
        return
    
    # Générer le rapport
    report_path = monitor.generate_html_report(df)
    
    logger.info(f"""
    ╔══════════════════════════════════════════════════════╗
    ║         RAPPORT DE MONITORING GÉNÉRÉ                 ║
    ╠══════════════════════════════════════════════════════╣
    ║ Conversations analysées: {len(df):4d}                      ║
    ║ Rapport disponible:                                  ║
    ║ {report_path}
    ╚══════════════════════════════════════════════════════╝
    """)
    
    logger.info("\n💡 Pour visualiser le rapport, ouvrez le fichier HTML dans votre navigateur")


if __name__ == "__main__":
    main()
