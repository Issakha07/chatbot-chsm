"""
Script de test pour simuler une alerte critique et tester l'envoi d'email
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.notifications import NotificationManager
from datetime import datetime

def test_critical_alert():
    """Simuler une alerte critique"""
    print("\n=== TEST D'ALERTE CRITIQUE ===\n")
    
    # Créer le gestionnaire de notifications
    notif = NotificationManager()
    
    # Simuler un rapport d'alerte critique
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'critical',
        'period_days': 1,
        'total_conversations': 15,
        'alerts': [
            {
                'metric': 'confidence',
                'status': 'critical',
                'message': 'CRITIQUE: Confiance moyenne (65.0%) sous le seuil (70.0%)',
                'avg_value': 0.65,
                'threshold': 0.70
            },
            {
                'metric': 'response_time',
                'status': 'warning',
                'message': 'ATTENTION: 25.0% des réponses sont lentes',
                'avg_value': 2.5,
                'threshold': 3.0
            }
        ],
        'anomalies': [
            {
                'type': 'duplicate_answers',
                'message': 'Réponse(s) identique(s) répétée(s) plus de 50% du temps'
            }
        ]
    }
    
    print("Envoi d'une alerte critique de test...")
    success = notif.notify_quality_alert(test_report)
    
    if success:
        print("\n✅ Alerte envoyée avec succès!")
        print("\nVérifiez votre boîte email:", notif.config['email']['recipients'])
    else:
        print("\n❌ Erreur lors de l'envoi de l'alerte")
    
    print("\n" + "="*60 + "\n")

def test_warning_alert():
    """Simuler une alerte warning"""
    print("\n=== TEST D'ALERTE WARNING ===\n")
    
    notif = NotificationManager()
    
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'warning',
        'period_days': 1,
        'total_conversations': 8,
        'alerts': [
            {
                'metric': 'volume',
                'status': 'warning',
                'message': 'ATTENTION: Volume faible (8 conversations, minimum: 5)',
                'value': 8,
                'threshold': 5
            }
        ],
        'anomalies': []
    }
    
    print("Envoi d'une alerte warning de test...")
    success = notif.notify_quality_alert(test_report)
    
    if success:
        print("\n✅ Alerte envoyée avec succès!")
    else:
        print("\n❌ Erreur lors de l'envoi de l'alerte")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("\nCe script va tester l'envoi d'alertes par email.")
    print("Assurez-vous que notification_config.json est bien configuré.\n")
    
    # Test alerte critique (devrait envoyer un email)
    test_critical_alert()
    
    # Test alerte warning (n'envoie pas d'email par défaut, seulement Teams)
    # test_warning_alert()
    
    print("\nTests terminés!")
