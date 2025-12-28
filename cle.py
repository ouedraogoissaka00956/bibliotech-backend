import secrets
import string

def generate_secret_key(length=64):
    """Génère une clé secrète sécurisée pour Flask"""
    
    # Utiliser tous les caractères possibles
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Générer une clé aléatoire
    secret_key = ''.join(secrets.choice(characters) for _ in range(length))
    
    return secret_key

def generate_multiple_keys():
    """Génère plusieurs clés et affiche les instructions"""
    
    print("\n" + "="*70)
    print(" GÉNÉRATEUR DE CLÉ SECRÈTE FLASK")
    print("="*70 + "\n")
    
    # Générer 3 clés différentes
    for i in range(1, 4):
        key = generate_secret_key()
        print(f"Clé #{i}:")
        print(f"{key}\n")
    
    print("="*70)
    print("\n INSTRUCTIONS:")
    print("\n1. Copiez UNE des clés ci-dessus")
    print("2. Ouvrez votre fichier .env")
    print("3. Ajoutez ou modifiez la ligne:")
    print("   SECRET_KEY=votre_clé_copiée_ici")
    print("\n  IMPORTANT:")
    print("   • Ne partagez JAMAIS cette clé")
    print("   • Ne la commitez JAMAIS sur Git")
    print("   • Utilisez une clé différente pour chaque environnement")
    print("   • Plus la clé est longue, plus c'est sécurisé")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    generate_multiple_keys()