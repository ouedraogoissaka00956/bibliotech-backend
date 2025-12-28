import os
from datetime import datetime

def check_backups():
    """Affiche toutes les sauvegardes disponibles"""
    
    backup_folder = 'backups'
    
    if not os.path.exists(backup_folder):
        print(" Dossier de sauvegarde introuvable")
        return
    
    # Récupérer toutes les sauvegardes
    backups = [
        f for f in os.listdir(backup_folder) 
        if f.startswith('bibliotech_auto_') and f.endswith('.db')
    ]
    
    if not backups:
        print(" Aucune sauvegarde automatique trouvée")
        return
    
    # Trier par date (plus récent en premier)
    backups.sort(reverse=True)
    
    print("\n" + "="*80)
    print(" SAUVEGARDES AUTOMATIQUES DISPONIBLES")
    print("="*80 + "\n")
    
    total_size = 0
    
    for i, backup in enumerate(backups, 1):
        filepath = os.path.join(backup_folder, backup)
        size = os.path.getsize(filepath) / 1024  # KB
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        total_size += size
        
        # Extraire la date du nom de fichier
        date_str = backup.replace('bibliotech_auto_', '').replace('.db', '')
        formatted_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S').strftime('%d/%m/%Y à %H:%M:%S')
        
        print(f"  {i:2d}.  {formatted_date}")
        print(f"       Taille : {size:.2f} KB")
        print(f"       Fichier : {backup}")
        
        # Indiquer si c'est la plus récente
        if i == 1:
            print(f"       PLUS RÉCENTE")
        
        print()
    
    print("="*80)
    print(f" Total : {len(backups)} sauvegarde(s)")
    print(f" Espace total : {total_size:.2f} KB ({total_size/1024:.2f} MB)")
    print("="*80 + "\n")
    
    # Recommandations
    if len(backups) < 5:
        print("  ATTENTION : Peu de sauvegardes disponibles")
        print("   Recommandation : Attendez quelques jours pour avoir un historique")
    elif len(backups) >= 30:
        print(" Bon historique de sauvegardes")
        print("   Les plus anciennes sont automatiquement supprimées")

if __name__ == '__main__':
    check_backups()