import os
from datetime import timedelta

class Config:
    # ============ SÉCURITÉ ============
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # ============ BASE DE DONNÉES ============
    # Détection automatique de l'environnement
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Render utilise postgres:// mais SQLAlchemy nécessite postgresql://
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Par défaut SQLite en local, PostgreSQL en production
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///bibliotech.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Options pour PostgreSQL
    if DATABASE_URL:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20
        }
    
    # ============ SESSIONS UTILISATEUR ============
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=365 * 100)
    
    # Se souvenir de moi
    REMEMBER_COOKIE_DURATION = timedelta(days=365 * 100)
    REMEMBER_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True
    
    # ============ UPLOADS ============
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # ============ EMAIL ============
    MAIL_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('SMTP_USERNAME')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('SMTP_USERNAME')
    MAIL_DEBUG = False
    
    # ============ SÉCURITÉ DES MOTS DE PASSE ============
    BCRYPT_LOG_ROUNDS = 12
    
    # ============ CORS ============
    # À modifier avec votre domaine frontend
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://bibliotech-frontend.vercel.app/').split(',')
    CORS_SUPPORTS_CREDENTIALS = True