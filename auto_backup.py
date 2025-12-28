import shutil
import os
import threading
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class AutoBackupService:
    """Service de sauvegarde automatique de la base de données"""
    
    def __init__(self, db_path='instance/bibliotech.db', backup_folder='backups', keep_backups=30):
        self.db_path = db_path
        self.backup_folder = backup_folder
        self.keep_backups = keep_backups
        self.scheduler = BackgroundScheduler()
        
        # Créer le dossier de sauvegarde
        os.makedirs(self.backup_folder, exist_ok=True)
        
    def create_backup(self):
        """Crée une sauvegarde de la base de données"""
        try:
            if not os.path.exists(self.db_path):
                print(f"  Base de données introuvable : {self.db_path}")
                return False
            
            # Nom du fichier de sauvegarde avec date et heure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_folder, f'bibliotech_auto_{timestamp}.db')
            
            # Copier la base de données
            shutil.copy2(self.db_path, backup_file)
            
            # Taille du fichier
            size = os.path.getsize(backup_file) / 1024  # En KB
            
            print(f" Sauvegarde automatique créée : {backup_file}")
            print(f" Taille : {size:.2f} KB")
            print(f" Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Nettoyer les anciennes sauvegardes
            self.cleanup_old_backups()
            
            return True
            
        except Exception as e:
            print(f" Erreur lors de la sauvegarde automatique : {str(e)}")
            return False
    
    def cleanup_old_backups(self):
        """Supprime les anciennes sauvegardes en gardant les N plus récentes"""
        try:
            # Lister tous les fichiers de sauvegarde automatique
            backups = [
                os.path.join(self.backup_folder, f) 
                for f in os.listdir(self.backup_folder) 
                if f.startswith('bibliotech_auto_') and f.endswith('.db')
            ]
            
            # Trier par date de modification (plus récent en premier)
            backups.sort(key=os.path.getmtime, reverse=True)
            
            # Supprimer les anciennes sauvegardes
            deleted_count = 0
            for old_backup in backups[self.keep_backups:]:
                os.remove(old_backup)
                deleted_count += 1
                print(f"  Ancienne sauvegarde supprimée : {os.path.basename(old_backup)}")
            
            if deleted_count > 0:
                print(f" {len(backups[:self.keep_backups])} sauvegarde(s) conservée(s)")
                
        except Exception as e:
            print(f"  Erreur lors du nettoyage : {str(e)}")
    
    def start_daily_backup(self, hour=2, minute=0):
        """
        Lance une sauvegarde quotidienne à une heure précise
        Par défaut : tous les jours à 2h00 du matin
        """
        self.scheduler.add_job(
            self.create_backup,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='daily_backup',
            name='Sauvegarde quotidienne',
            replace_existing=True
        )
        print(f" Sauvegarde quotidienne programmée à {hour:02d}:{minute:02d}")
    
    def start_hourly_backup(self):
        """Lance une sauvegarde toutes les heures"""
        self.scheduler.add_job(
            self.create_backup,
            trigger='interval',
            hours=1,
            id='hourly_backup',
            name='Sauvegarde horaire',
            replace_existing=True
        )
        print(" Sauvegarde horaire activée")
    
    def start_interval_backup(self, minutes=30):
        """
        Lance une sauvegarde à intervalle régulier
        Par défaut : toutes les 30 minutes
        """
        self.scheduler.add_job(
            self.create_backup,
            trigger='interval',
            minutes=minutes,
            id='interval_backup',
            name=f'Sauvegarde toutes les {minutes} minutes',
            replace_existing=True
        )
        print(f" Sauvegarde automatique toutes les {minutes} minutes")
    
    def start(self):
        """Démarre le service de sauvegarde"""
        if not self.scheduler.running:
            self.scheduler.start()
            print(" Service de sauvegarde automatique démarré")
            
            # Créer une sauvegarde immédiate au démarrage
            print("\n Création d'une sauvegarde initiale...")
            self.create_backup()
        else:
            print("  Le service de sauvegarde est déjà en cours d'exécution")
    
    def stop(self):
        """Arrête le service de sauvegarde"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print(" Service de sauvegarde automatique arrêté")
    
    def get_backup_info(self):
        """Retourne des informations sur les sauvegardes"""
        try:
            backups = [
                f for f in os.listdir(self.backup_folder) 
                if f.startswith('bibliotech_auto_') and f.endswith('.db')
            ]
            
            total_size = sum(
                os.path.getsize(os.path.join(self.backup_folder, f)) 
                for f in backups
            ) / (1024 * 1024)  # En MB
            
            return {
                'count': len(backups),
                'total_size_mb': round(total_size, 2),
                'latest': max(backups) if backups else None
            }
        except Exception as e:
            print(f"  Erreur lors de la récupération des infos : {str(e)}")
            return {'count': 0, 'total_size_mb': 0, 'latest': None}


# Instance globale du service
backup_service = None

def init_backup_service(app, mode='daily', **kwargs):
    """
    Initialise le service de sauvegarde automatique
    
    Args:
        app: Instance Flask
        mode: 'daily' (quotidien), 'hourly' (horaire), ou 'interval' (intervalle)
        **kwargs: Arguments supplémentaires selon le mode
            - Pour 'daily': hour=2, minute=0
            - Pour 'interval': minutes=30
    """
    global backup_service
    
    with app.app_context():
        backup_service = AutoBackupService(keep_backups=50)
        
        if mode == 'daily':
            hour = kwargs.get('hour', 2)
            minute = kwargs.get('minute', 0)
            backup_service.start_daily_backup(hour=hour, minute=minute)
        
        elif mode == 'hourly':
            backup_service.start_hourly_backup()
        
        elif mode == 'interval':
            minutes = kwargs.get('minutes', 30)
            backup_service.start_interval_backup(minutes=minutes)
        
        else:
            print(f"  Mode de sauvegarde inconnu : {mode}")
            return None
        
        backup_service.start()
        
        print("\n" + "="*70)
        print(" SERVICE DE SAUVEGARDE AUTOMATIQUE")
        print("="*70)
        info = backup_service.get_backup_info()
        print(f" Sauvegardes existantes : {info['count']}")
        print(f" Espace utilisé : {info['total_size_mb']} MB")
        if info['latest']:
            print(f" Dernière sauvegarde : {info['latest']}")
        print("="*70 + "\n")
        
        return backup_service