from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
import random

db = SQLAlchemy()
bcrypt = Bcrypt()

class Utilisateur(UserMixin, db.Model):
    __tablename__ = 'utilisateurs'
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='utilisateur')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Photo de profil
    photo_profil = db.Column(db.String(255), default='default.png')
    
    # Code de récupération mot de passe
    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expiration = db.Column(db.DateTime, nullable=True)
    
    # NOUVEAU : Vérification d'email
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    verification_token_expiration = db.Column(db.DateTime, nullable=True)
    
    livres = db.relationship('Livre', backref='proprietaire', lazy=True, cascade='all, delete-orphan')
    membres = db.relationship('Membre', backref='proprietaire', lazy=True, cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.id_utilisateur)
    
    def set_password(self, password):
        self.mot_de_passe = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)
    
    def generate_reset_code(self):
        """Génère un code à 6 chiffres pour la réinitialisation de mot de passe"""
        self.reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.reset_code_expiration = datetime.utcnow() + timedelta(minutes=15)
        return self.reset_code
    
    def generate_verification_token(self):
        """Génère un token de vérification d'email sécurisé"""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expiration = datetime.utcnow() + timedelta(hours=24)  # Valide 24h
        return self.verification_token
    
    def verify_email_token(self, token):
        """Vérifie le token de vérification d'email"""
        if not self.verification_token or not self.verification_token_expiration:
            return False
        if datetime.utcnow() > self.verification_token_expiration:
            return False
        return self.verification_token == token
    
    def to_dict(self):
        return {
            'id_utilisateur': self.id_utilisateur,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'role': self.role,
            'photo_profil': self.photo_profil,
            'email_verified': self.email_verified,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M:%S') if self.date_creation else None
        }

# Autres modèles restent identiques
class Livre(db.Model):
    __tablename__ = 'livres'
    id_livre = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    auteur = db.Column(db.String(255), nullable=False)
    categorie = db.Column(db.String(100))
    annee_publication = db.Column(db.Integer)
    nombre_exemplaires = db.Column(db.Integer, default=1)
    disponibles = db.Column(db.Integer, default=1)
    id_utilisateur = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur'), nullable=False)
    
    emprunts = db.relationship('Emprunt', backref='livre', lazy=True)
    reservations = db.relationship('Reservation', backref='livre', lazy=True)

    def to_dict(self):
        return {
            'id_livre': self.id_livre,
            'titre': self.titre,
            'auteur': self.auteur,
            'categorie': self.categorie,
            'annee_publication': self.annee_publication,
            'nombre_exemplaires': self.nombre_exemplaires,
            'disponibles': self.disponibles
        }

class Membre(db.Model):
    __tablename__ = 'membres'
    id_membre = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    date_inscription = db.Column(db.Date, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='actif')
    id_utilisateur = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_utilisateur'), nullable=False)
    
    emprunts = db.relationship('Emprunt', backref='membre', lazy=True)
    reservations = db.relationship('Reservation', backref='membre', lazy=True)

    def to_dict(self):
        return {
            'id_membre': self.id_membre,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'date_inscription': self.date_inscription.strftime('%Y-%m-%d') if self.date_inscription else None,
            'statut': self.statut,
            'id_utilisateur': self.id_utilisateur
        }

class Emprunt(db.Model):
    __tablename__ = 'emprunts'
    id_emprunt = db.Column(db.Integer, primary_key=True)
    id_livre = db.Column(db.Integer, db.ForeignKey('livres.id_livre'), nullable=False)
    id_membre = db.Column(db.Integer, db.ForeignKey('membres.id_membre'), nullable=False)
    date_emprunt = db.Column(db.Date, default=datetime.utcnow)
    date_retour_prevue = db.Column(db.Date, nullable=False)
    date_retour_reelle = db.Column(db.Date)
    statut = db.Column(db.String(20), default='en_cours')
    
    amendes = db.relationship('Amende', backref='emprunt', lazy=True)

    def to_dict(self):
        return {
            'id_emprunt': self.id_emprunt,
            'id_livre': self.id_livre,
            'id_membre': self.id_membre,
            'livre': self.livre.to_dict() if self.livre else None,
            'membre': self.membre.to_dict() if self.membre else None,
            'date_emprunt': self.date_emprunt.strftime('%Y-%m-%d') if self.date_emprunt else None,
            'date_retour_prevue': self.date_retour_prevue.strftime('%Y-%m-%d') if self.date_retour_prevue else None,
            'date_retour_reelle': self.date_retour_reelle.strftime('%Y-%m-%d') if self.date_retour_reelle else None,
            'statut': self.statut
        }

class Amende(db.Model):
    __tablename__ = 'amendes'
    id_amende = db.Column(db.Integer, primary_key=True)
    id_emprunt = db.Column(db.Integer, db.ForeignKey('emprunts.id_emprunt'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(20), default='impayee')
    date_creation = db.Column(db.Date, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id_amende': self.id_amende,
            'id_emprunt': self.id_emprunt,
            'emprunt': self.emprunt.to_dict() if self.emprunt else None,
            'montant': self.montant,
            'statut': self.statut,
            'date_creation': self.date_creation.strftime('%Y-%m-%d') if self.date_creation else None
        }

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id_reservation = db.Column(db.Integer, primary_key=True)
    id_livre = db.Column(db.Integer, db.ForeignKey('livres.id_livre'), nullable=False)
    id_membre = db.Column(db.Integer, db.ForeignKey('membres.id_membre'), nullable=False)
    date_reservation = db.Column(db.Date, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='en_attente')

    def to_dict(self):
        return {
            'id_reservation': self.id_reservation,
            'id_livre': self.id_livre,
            'id_membre': self.id_membre,
            'livre': self.livre.to_dict() if self.livre else None,
            'membre': self.membre.to_dict() if self.membre else None,
            'date_reservation': self.date_reservation.strftime('%Y-%m-%d') if self.date_reservation else None,
            'statut': self.statut
        }