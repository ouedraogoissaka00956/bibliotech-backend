import shutil
import os
from datetime import datetime

def backup_database():
    """Crée une sauvegarde de la base de données"""
    
    # Fichier source
    db_file = 'instance/bibliotech.db'
    
    # Vérifier si la base existe
    if not os.path.exists(db_file):
        print(" Base de données introuvable")
        return False
    
    # Créer le dossier de sauvegarde
    backup_folder = 'backups'
    os.makedirs(backup_folder, exist_ok=True)
    
    # Nom du fichier de sauvegarde avec date et heure
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_folder, f'bibliotech_backup_{timestamp}.db')
    
    try:
        # Copier la base de données
        shutil.copy2(db_file, backup_file)
        
        # Taille du fichier
        size = os.path.getsize(backup_file) / 1024  # En KB
        
        print(f" Sauvegarde créée : {backup_file}")
        print(f" Taille : {size:.2f} KB")
        
        # Nettoyer les anciennes sauvegardes (garder les 10 dernières)
        cleanup_old_backups(backup_folder)
        
        return True
        
    except Exception as e:
        print(f" Erreur lors de la sauvegarde : {str(e)}")
        return False

def cleanup_old_backups(backup_folder, keep=10):
    """Supprime les anciennes sauvegardes en gardant les N plus récentes"""
    try:
        # Lister tous les fichiers de sauvegarde
        backups = [
            os.path.join(backup_folder, f) 
            for f in os.listdir(backup_folder) 
            if f.startswith('bibliotech_backup_') and f.endswith('.db')
        ]
        
        # Trier par date de modification (plus récent en premier)
        backups.sort(key=os.path.getmtime, reverse=True)
        
        # Supprimer les anciennes sauvegardes
        for old_backup in backups[keep:]:
            os.remove(old_backup)
            print(f"🗑  Ancienne sauvegarde supprimée : {os.path.basename(old_backup)}")
            
    except Exception as e:
        print(f"  Erreur lors du nettoyage : {str(e)}")

def restore_database(backup_file):
    """Restaure la base de données depuis une sauvegarde"""
    
    db_file = 'instance/bibliotech.db'
    
    if not os.path.exists(backup_file):
        print(f" Fichier de sauvegarde introuvable : {backup_file}")
        return False
    
    try:
        # Créer une sauvegarde de la base actuelle avant restauration
        if os.path.exists(db_file):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_backup = f'instance/bibliotech_before_restore_{timestamp}.db'
            shutil.copy2(db_file, temp_backup)
            print(f" Sauvegarde de sécurité créée : {temp_backup}")
        
        # Restaurer
        shutil.copy2(backup_file, db_file)
        print(f" Base de données restaurée depuis : {backup_file}")
        return True
        
    except Exception as e:
        print(f" Erreur lors de la restauration : {str(e)}")
        return False

def list_backups():
    """Liste toutes les sauvegardes disponibles"""
    backup_folder = 'backups'
    
    if not os.path.exists(backup_folder):
        print(" Aucun dossier de sauvegarde trouvé")
        return
    
    backups = [
        f for f in os.listdir(backup_folder) 
        if f.startswith('bibliotech_backup_') and f.endswith('.db')
    ]
    
    if not backups:
        print(" Aucune sauvegarde trouvée")
        return
    
    print(f"\n {len(backups)} sauvegarde(s) disponible(s):\n")
    
    for backup in sorted(backups, reverse=True):
        filepath = os.path.join(backup_folder, backup)
        size = os.path.getsize(filepath) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"  • {backup}")
        print(f"    Taille: {size:.2f} KB")
        print(f"    Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'backup':
            backup_database()
        
        elif command == 'restore' and len(sys.argv) > 2:
            backup_file = sys.argv[2]
            restore_database(backup_file)
        
        elif command == 'list':
            list_backups()
        
        else:
            print("Usage:")
            print("  python backup.py backup              # Créer une sauvegarde")
            print("  python backup.py list                # Lister les sauvegardes")
            print("  python backup.py restore <fichier>   # Restaurer une sauvegarde")
    else:
        # Par défaut, créer une sauvegarde
        backup_database()