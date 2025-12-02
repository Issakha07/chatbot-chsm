"""
Script pour générer des clés API uniques pour les clients
"""
import secrets

def generate_api_key(plan: str = "business", client_name: str = "") -> str:
    """
    Génère une clé API unique
    
    Args:
        plan: Type de plan (demo, starter, business, enterprise)
        client_name: Nom du client (optionnel)
    
    Returns:
        Clé API au format: sk_{plan}_{random_string}
    """
    random_part = secrets.token_urlsafe(32)  # 43 caractères
    return f"sk_{plan}_{random_part}"

def generate_client_package(client_name: str, plan: str, email: str):
    """
    Génère les informations complètes pour un nouveau client
    """
    api_key = generate_api_key(plan, client_name)
    
    # Quotas selon le plan
    quotas = {
        "demo": {"monthly": 100, "per_minute": 5, "price": "Gratuit (30 jours)"},
        "starter": {"monthly": 1000, "per_minute": 10, "price": "99€/mois"},
        "business": {"monthly": 10000, "per_minute": 30, "price": "299€/mois"},
        "enterprise": {"monthly": "Illimité", "per_minute": 100, "price": "999€/mois"}
    }
    
    info = f"""
================================================================================
NOUVELLE CLÉ API GÉNÉRÉE - {client_name.upper()}
================================================================================

📧 Client: {email}
📦 Plan: {plan.capitalize()}
🔑 Clé API: {api_key}

📊 QUOTAS:
   - Requêtes mensuelles: {quotas[plan]["monthly"]}
   - Requêtes par minute: {quotas[plan]["per_minute"]}
   - Tarif: {quotas[plan]["price"]}

⚙️ CONFIGURATION CLIENT (.env):

BACKEND_API_URL=https://votre-api.onrender.com/api/chat
API_KEY={api_key}

📝 À FAIRE:
   1. Ajouter la clé dans backend/app.py:
      VALID_API_KEYS = {{
          "{client_name}": "{api_key}",
      }}
   
   2. Commit et push pour redéployer
   
   3. Créer le ZIP client:
      - interface-streamlit.py
      - style.css
      - requirements.txt
      - README.md
      - LICENSE.txt
      - API_KEY.txt (avec la clé ci-dessus)
   
   4. Envoyer par email au client
   
   5. Facturer: {quotas[plan]["price"]}

================================================================================
Date de création: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================
    """
    
    return info

# ==========================================
# EXEMPLES D'UTILISATION
# ==========================================

if __name__ == "__main__":
    import sys
    
    print("🔐 GÉNÉRATEUR DE CLÉS API - CHATBOT IT SUPPORT\n")
    
    # Exemple 1: Clé simple
    print("Exemple 1: Clé Business simple")
    key1 = generate_api_key("business")
    print(f"   → {key1}\n")
    
    # Exemple 2: Package client complet
    print("Exemple 2: Package client complet")
    print(generate_client_package(
        client_name="hopital_chsm",
        plan="business",
        email="it@hopital-chsm.qc.ca"
    ))
    
    # Exemple 3: Générer plusieurs clés
    print("\nExemple 3: Générer 3 clés de démo")
    for i in range(3):
        key = generate_api_key("demo")
        print(f"   Démo {i+1}: {key}")
    
    # Mode interactif
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("\n" + "="*80)
        print("MODE INTERACTIF")
        print("="*80 + "\n")
        
        client_name = input("Nom du client (ex: hopital_xyz): ")
        email = input("Email du client: ")
        
        print("\nPlans disponibles:")
        print("  1. Demo (100 req/mois, gratuit 30 jours)")
        print("  2. Starter (1000 req/mois, 99€/mois)")
        print("  3. Business (10000 req/mois, 299€/mois)")
        print("  4. Enterprise (illimité, 999€/mois)")
        
        plan_choice = input("\nChoisissez un plan (1-4): ")
        plans = ["demo", "starter", "business", "enterprise"]
        plan = plans[int(plan_choice) - 1] if plan_choice.isdigit() and 1 <= int(plan_choice) <= 4 else "demo"
        
        print("\n")
        print(generate_client_package(client_name, plan, email))
        
        # Sauvegarder dans un fichier
        save = input("\nSauvegarder dans un fichier? (o/n): ")
        if save.lower() == 'o':
            filename = f"api_key_{client_name}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(generate_client_package(client_name, plan, email))
            print(f"✅ Sauvegardé dans: {filename}")
