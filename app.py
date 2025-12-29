from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from config import Config
from models import db, bcrypt, Utilisateur, Livre, Membre, Emprunt, Amende, Reservation
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import os
import secrets
from dotenv import load_dotenv
import atexit
load_dotenv()


app = Flask(__name__)
app.config.from_object(Config)

# Configuration Mail
app.config['MAIL_SERVER'] = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('SMTP_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('SMTP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('SMTP_USERNAME')
app.config['MAIL_DEBUG'] = True

mail = Mail(app)

# S'assurer que le dossier uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_profile_picture(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', unique_filename)
        
        img = Image.open(file)
        img.thumbnail((300, 300))
        img.save(filepath)
        
        return unique_filename
    return None

def send_reset_code_email(user_email, user_name, reset_code):
    """Envoie le code de réinitialisation par email"""
    try:
        msg = Message(
            subject=" Code de réinitialisation - BiblioTech",
            recipients=[user_email]
        )
        
        # Template HTML de l'email
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f0f9ff;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
                    padding: 40px 20px;
                    text-align: center;
                    color: white;
                }}
                .logo {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #1e40af;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #4b5563;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .code-box {{
                    background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
                    border: 3px solid #3b82f6;
                    border-radius: 12px;
                    padding: 30px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code-label {{
                    font-size: 14px;
                    color: #1e40af;
                    font-weight: 600;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .code {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #1e3a8a;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .warning-text {{
                    font-size: 14px;
                    color: #92400e;
                    line-height: 1.5;
                }}
                .expiry {{
                    text-align: center;
                    color: #ef4444;
                    font-weight: 600;
                    font-size: 14px;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 30px;
                    text-align: center;
                    border-top: 2px solid #e5e7eb;
                }}
                .footer-text {{
                    font-size: 13px;
                    color: #6b7280;
                    line-height: 1.6;
                }}
                .security-badge {{
                    display: inline-block;
                    background: #dcfce7;
                    color: #166534;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo"></div>
                    <h1>BiblioTech</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Système de Gestion de Bibliothèque</p>
                </div>
                
                <div class="content">
                    <div class="greeting">
                        Bonjour <strong>{user_name}</strong> 
                    </div>
                    
                    <div class="message">
                        Vous avez demandé la réinitialisation de votre mot de passe. 
                        Voici votre code de vérification :
                    </div>
                    
                    <div class="code-box">
                        <div class="code-label">Votre code de vérification</div>
                        <div class="code">{reset_code}</div>
                    </div>
                    
                    <div class="expiry">
                         Ce code expire dans 15 minutes
                    </div>
                    
                    <div class="warning">
                        <div class="warning-text">
                            <strong>⚠ Important :</strong><br>
                            • Ne partagez jamais ce code avec personne<br>
                            • Si vous n'avez pas demandé cette réinitialisation, ignorez cet email<br>
                            • Ce code est à usage unique
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-text">
                        Cet email a été envoyé automatiquement par BiblioTech.<br>
                        Si vous avez des questions, contactez notre support.
                    </div>
                    <div class="security-badge">
                         Connexion sécurisée
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f" Email envoyé avec succès à {user_email}")
        return True
        
    except Exception as e:
        print(f" Erreur lors de l'envoi de l'email: {str(e)}")
        return False

from flask_cors import CORS

CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": [
            "https://bibliotech-frontend.vercel.app"
        ]
    }
})


db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))
 
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({
        "error": "Non authentifié"
    }), 401


with app.app_context():
    # NE PLUS SUPPRIMER LES DONNÉES À CHAQUE DÉMARRAGE
    # db.drop_all()  #  COMMENTÉ POUR GARDER LES DONNÉES
    
    # Créer les tables si elles n'existent pas
    db.create_all()
    
    #  MODE PRODUCTION : Pas d'utilisateurs de test
    print(" Base de données initialisée!")
    print(f" Utilisateurs enregistrés : {Utilisateur.query.count()}")
    print(f" Livres dans le catalogue : {Livre.query.count()}")
    print(f" Membres actifs : {Membre.query.count()}")

# ============ SAUVEGARDE AUTOMATIQUE ============
from auto_backup import init_backup_service

# Option 3 : Sauvegarde automatique toutes les 30 minutes
init_backup_service(app, mode='interval', minutes=30)

# Arrêter proprement le service à la fermeture de l'application
from auto_backup import backup_service
if backup_service:
    atexit.register(backup_service.stop)

# ============ AUTHENTIFICATION ============
# ============ ROUTES PROFIL ============

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify(current_user.to_dict()), 200

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.json
    
    try:
        if data.get('email') and data['email'] != current_user.email:
            existing_user = Utilisateur.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
        if data.get('nom'):
            current_user.nom = data['nom']
        if data.get('prenom'):
            current_user.prenom = data['prenom']
        if data.get('email'):
            current_user.email = data['email']
        
        if data.get('nouveau_mot_de_passe'):
            if not data.get('ancien_mot_de_passe'):
                return jsonify({'error': 'Ancien mot de passe requis'}), 400
            
            if not current_user.check_password(data['ancien_mot_de_passe']):
                return jsonify({'error': 'Ancien mot de passe incorrect'}), 400
            
            current_user.set_password(data['nouveau_mot_de_passe'])
        
        db.session.commit()
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'utilisateur': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/profile/photo', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'Aucune photo fournie'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'error': 'Aucune photo sélectionnée'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format de fichier non autorisé'}), 400
    
    try:
        if current_user.photo_profil != 'default.png':
            old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', current_user.photo_profil)
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        filename = save_profile_picture(file)
        if filename:
            current_user.photo_profil = filename
            db.session.commit()
            
            return jsonify({
                'message': 'Photo de profil mise à jour',
                'photo_profil': filename
            }), 200
        else:
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/uploads/profiles/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), filename)

# ============ RÉCUPÉRATION MOT DE PASSE AVEC EMAIL ============

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Génère et envoie un code de réinitialisation par email"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    utilisateur = Utilisateur.query.filter_by(email=email).first()
    
    # Pour la sécurité, on ne révèle pas si l'email existe ou non
    if not utilisateur:
        return jsonify({
            'message': 'Si cet email existe, un code de réinitialisation a été envoyé'
        }), 200
    
    try:
        # Générer le code à 6 chiffres
        code = utilisateur.generate_reset_code()
        db.session.commit()
        
        # Envoyer l'email
        user_name = f"{utilisateur.prenom} {utilisateur.nom}"
        email_sent = send_reset_code_email(utilisateur.email, user_name, code)
        
        if email_sent:
            print(f" Code envoyé à {utilisateur.email}: {code}")
            return jsonify({
                'message': 'Un code de vérification a été envoyé à votre adresse email',
                'email': email
            }), 200
        else:
            # En cas d'erreur d'envoi, afficher le code dans la console (développement uniquement)
            print(f"\n{'='*60}")
            print(f"  ERREUR D'ENVOI EMAIL - CODE DE DÉVELOPPEMENT")
            print(f"{'='*60}")
            print(f"Email: {utilisateur.email}")
            print(f"Code: {code}")
            print(f"Expire dans: 15 minutes")
            print(f"{'='*60}\n")
            
            return jsonify({
                'error': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.',
                'dev_code': code if app.debug else None
            }), 500
            
    except Exception as e:
        db.session.rollback()
        print(f" Erreur: {str(e)}")
        return jsonify({'error': 'Erreur lors de la génération du code'}), 500

@app.route('/api/auth/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """Vérifie le code de réinitialisation"""
    data = request.json
    email = data.get('email')
    code = data.get('code')
    
    if not email or not code:
        return jsonify({'error': 'Email et code requis'}), 400
    
    utilisateur = Utilisateur.query.filter_by(email=email).first()
    
    if not utilisateur:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    if not utilisateur.reset_code:
        return jsonify({'error': 'Aucun code de réinitialisation actif'}), 400
    
    if utilisateur.reset_code_expiration < datetime.utcnow():
        return jsonify({'error': 'Code expiré. Demandez un nouveau code'}), 400
    
    if utilisateur.reset_code != code:
        return jsonify({'error': 'Code incorrect'}), 400
    
    return jsonify({
        'message': 'Code valide',
        'valid': True
    }), 200

@app.route('/api/auth/reset-password-with-code', methods=['POST'])
def reset_password_with_code():
    """Réinitialise le mot de passe avec le code"""
    data = request.json
    email = data.get('email')
    code = data.get('code')
    nouveau_mot_de_passe = data.get('mot_de_passe')
    
    if not email or not code or not nouveau_mot_de_passe:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    if len(nouveau_mot_de_passe) < 6:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
    
    utilisateur = Utilisateur.query.filter_by(email=email).first()
    
    if not utilisateur:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    if not utilisateur.reset_code:
        return jsonify({'error': 'Aucun code de réinitialisation actif'}), 400
    
    if utilisateur.reset_code_expiration < datetime.utcnow():
        return jsonify({'error': 'Code expiré'}), 400
    
    if utilisateur.reset_code != code:
        return jsonify({'error': 'Code incorrect'}), 400
    
    try:
        utilisateur.set_password(nouveau_mot_de_passe)
        utilisateur.reset_code = None
        utilisateur.reset_code_expiration = None
        db.session.commit()
        
        print(f" Mot de passe réinitialisé pour {utilisateur.email}")
        
        return jsonify({'message': 'Mot de passe réinitialisé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f" Erreur: {str(e)}")
        return jsonify({'error': str(e)}), 400
    

def send_verification_email(user_email, user_name, verification_token):
    """Envoie l'email de vérification avec un bouton de confirmation"""
    try:
        # URL de vérification (à adapter selon votre domaine)
        verification_url = f"http://localhost:5173/verify-email?token={verification_token}"
        
        msg = Message(
            subject=" Confirmez votre inscription - BiblioTech",
            recipients=[user_email]
        )
        
        # Template HTML de l'email
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f0f9ff;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    padding: 40px 20px;
                    text-align: center;
                    color: white;
                }}
                .logo {{
                    font-size: 64px;
                    margin-bottom: 10px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 20px;
                    color: #047857;
                    margin-bottom: 20px;
                    font-weight: bold;
                }}
                .message {{
                    font-size: 16px;
                    color: #4b5563;
                    line-height: 1.8;
                    margin-bottom: 30px;
                }}
                .button-container {{
                    text-align: center;
                    margin: 40px 0;
                }}
                .verify-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    text-decoration: none;
                    padding: 18px 50px;
                    border-radius: 12px;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
                    transition: transform 0.2s;
                }}
                .verify-button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
                }}
                .info-box {{
                    background: #ecfdf5;
                    border-left: 4px solid #10b981;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 30px 0;
                }}
                .info-text {{
                    font-size: 14px;
                    color: #065f46;
                    line-height: 1.6;
                    margin: 0;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .warning-text {{
                    font-size: 14px;
                    color: #92400e;
                    line-height: 1.5;
                    margin: 0;
                }}
                .expiry {{
                    text-align: center;
                    color: #dc2626;
                    font-weight: 600;
                    font-size: 14px;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 30px;
                    text-align: center;
                    border-top: 2px solid #e5e7eb;
                }}
                .footer-text {{
                    font-size: 13px;
                    color: #6b7280;
                    line-height: 1.6;
                }}
                .alternative-link {{
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    word-break: break-all;
                }}
                .alternative-link a {{
                    color: #3b82f6;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo"></div>
                    <h1>BiblioTech</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Bienvenue !</p>
                </div>
                
                <div class="content">
                    <div class="greeting">
                        Bonjour {user_name} ! 
                    </div>
                    
                    <div class="message">
                        <p><strong>Merci de vous être inscrit sur BiblioTech !</strong></p>
                        <p>Nous sommes ravis de vous accueillir dans notre communauté. Pour finaliser votre inscription et sécuriser votre compte, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous.</p>
                    </div>
                    
                    <div class="button-container">
                        <a href="{verification_url}" class="verify-button">
                             Vérifier mon adresse email
                        </a>
                    </div>
                    
                    <div class="info-box">
                        <p class="info-text">
                            <strong> Ce que vous pourrez faire après vérification :</strong><br><br>
                            • Gérer votre catalogue de livres<br>
                            • Ajouter et suivre vos membres<br>
                            • Gérer les emprunts et retours<br>
                            • Suivre les amendes et paiements<br>
                            • Accéder à toutes les fonctionnalités
                        </p>
                    </div>
                    
                    <div class="expiry">
                         Ce lien est valide pendant 24 heures
                    </div>
                    
                    <div class="warning">
                        <p class="warning-text">
                            <strong> Important :</strong><br>
                            • Si vous n'avez pas créé de compte, ignorez cet email<br>
                            • Ce lien ne peut être utilisé qu'une seule fois<br>
                            • Ne partagez jamais ce lien avec personne
                        </p>
                    </div>
                    
                    <div class="alternative-link">
                        <p style="font-size: 13px; color: #6b7280; margin: 0 0 10px 0;">
                            Le bouton ne fonctionne pas ? Copiez ce lien dans votre navigateur :
                        </p>
                        <a href="{verification_url}">{verification_url}</a>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-text">
                        Cet email a été envoyé automatiquement par BiblioTech.<br>
                        Si vous avez des questions, contactez notre support.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        print(f" Email de vérification envoyé à {user_email}")
        return True
        
    except Exception as e:
        print(f" Erreur lors de l'envoi de l'email de vérification: {str(e)}")
        return False    

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Inscription avec envoi d'email de vérification"""
    data = request.json
    
    # Vérifier si l'email existe déjà
    if Utilisateur.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cet email existe déjà'}), 400
    
    try:
        # Créer le nouvel utilisateur (NON vérifié)
        nouvel_utilisateur = Utilisateur(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            role='utilisateur',
            email_verified=False  # Pas encore vérifié
        )
        nouvel_utilisateur.set_password(data['mot_de_passe'])
        
        # Générer le token de vérification
        verification_token = nouvel_utilisateur.generate_verification_token()
        
        # Sauvegarder en base de données
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        
        # Envoyer l'email de vérification
        user_name = f"{nouvel_utilisateur.prenom} {nouvel_utilisateur.nom}"
        email_sent = send_verification_email(
            nouvel_utilisateur.email, 
            user_name, 
            verification_token
        )
        
        if email_sent:
            return jsonify({
                'message': 'Inscription réussie ! Vérifiez votre email pour activer votre compte.',
                'email': nouvel_utilisateur.email,
                'verification_required': True
            }), 201
        else:
            # Si l'envoi échoue, afficher le lien en console (développement)
            verification_url = f"http://localhost:5173/verify-email?token={verification_token}"
            print(f"\n{'='*70}")
            print(f"  ERREUR D'ENVOI EMAIL - LIEN DE VÉRIFICATION")
            print(f"{'='*70}")
            print(f"Email: {nouvel_utilisateur.email}")
            print(f"Lien: {verification_url}")
            print(f"Valide pendant: 24 heures")
            print(f"{'='*70}\n")
            
            return jsonify({
                'message': 'Inscription réussie ! Vérifiez votre email.',
                'warning': 'Erreur d\'envoi de l\'email. Contactez le support.',
                'dev_link': verification_url if app.debug else None
            }), 201
            
    except Exception as e:
        db.session.rollback()
        print(f" Erreur lors de l'inscription: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Vérifie l'email de l'utilisateur avec le token"""
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token manquant'}), 400
    
    try:
        # Rechercher l'utilisateur avec ce token
        utilisateur = Utilisateur.query.filter_by(verification_token=token).first()
        
        if not utilisateur:
            return jsonify({'error': 'Token invalide ou expiré'}), 404
        
        # Vérifier si déjà vérifié
        if utilisateur.email_verified:
            return jsonify({'message': 'Email déjà vérifié', 'already_verified': True}), 200
        
        # Vérifier le token
        if utilisateur.verify_email_token(token):
            # Activer le compte
            utilisateur.email_verified = True
            utilisateur.verification_token = None
            utilisateur.verification_token_expiration = None
            db.session.commit()
            
            print(f" Email vérifié pour {utilisateur.email}")
            
            return jsonify({
                'message': 'Email vérifié avec succès ! Vous pouvez maintenant vous connecter.',
                'success': True,
                'email': utilisateur.email
            }), 200
        else:
            return jsonify({'error': 'Token expiré. Demandez un nouveau lien de vérification.'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f" Erreur lors de la vérification: {str(e)}")
        return jsonify({'error': 'Erreur lors de la vérification'}), 500


@app.route('/api/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Renvoie l'email de vérification"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    try:
        utilisateur = Utilisateur.query.filter_by(email=email).first()
        
        if not utilisateur:
            # Ne pas révéler si l'email existe
            return jsonify({'message': 'Si cet email existe, un nouveau lien a été envoyé'}), 200
        
        if utilisateur.email_verified:
            return jsonify({'error': 'Cet email est déjà vérifié'}), 400
        
        # Générer un nouveau token
        verification_token = utilisateur.generate_verification_token()
        db.session.commit()
        
        # Renvoyer l'email
        user_name = f"{utilisateur.prenom} {utilisateur.nom}"
        email_sent = send_verification_email(utilisateur.email, user_name, verification_token)
        
        if email_sent:
            return jsonify({'message': 'Un nouveau lien de vérification a été envoyé'}), 200
        else:
            return jsonify({'error': 'Erreur lors de l\'envoi de l\'email'}), 500
            
    except Exception as e:
        db.session.rollback()
        print(f" Erreur: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Connexion avec vérification d'email obligatoire"""
    data = request.json
    
    utilisateur = Utilisateur.query.filter_by(email=data['email']).first()
    
    if not utilisateur or not utilisateur.check_password(data['mot_de_passe']):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
    
    # IMPORTANT : Vérifier si l'email est vérifié
    if not utilisateur.email_verified:
        return jsonify({
            'error': 'Veuillez vérifier votre email avant de vous connecter',
            'email_not_verified': True,
            'email': utilisateur.email
        }), 403
    
    # Email vérifié, connexion autorisée
    login_user(utilisateur, remember=True)
    
    return jsonify({
        'message': 'Connexion réussie',
        'utilisateur': utilisateur.to_dict()
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(current_user.to_dict()), 200

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Déconnexion réussie'}), 200


# ============ LIVRES ============

@app.route('/api/livres', methods=['GET'])
@login_required
def get_livres():
    search = request.args.get('search', '')
    query = Livre.query.filter_by(id_utilisateur=current_user.id_utilisateur)
    
    if search:
        query = query.filter(
            (Livre.titre.contains(search)) | 
            (Livre.auteur.contains(search)) 
        )
    
    return jsonify([livre.to_dict() for livre in query.all()])

@app.route('/api/livres', methods=['POST'])
@login_required
def create_livre():
    data = request.json
    try:
        nouveau_livre = Livre(
            titre=data['titre'],
            auteur=data['auteur'],
            categorie=data.get('categorie', ''),
            annee_publication=data.get('annee_publication'),
            nombre_exemplaires=data.get('nombre_exemplaires', 1),
            disponibles=data.get('nombre_exemplaires', 1),
            id_utilisateur=current_user.id_utilisateur
        )
        db.session.add(nouveau_livre)
        db.session.commit()
        return jsonify(nouveau_livre.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/livres/<int:id>', methods=['PUT'])
@login_required
def update_livre(id):
    livre = Livre.query.filter_by(id_livre=id, id_utilisateur=current_user.id_utilisateur).first()
    if not livre:
        return jsonify({'error': 'Livre non trouvé'}), 404
    
    data = request.json
    try:
        livre.titre = data.get('titre', livre.titre)
        livre.auteur = data.get('auteur', livre.auteur)
        livre.categorie = data.get('categorie', livre.categorie)
        livre.annee_publication = data.get('annee_publication', livre.annee_publication)
        livre.nombre_exemplaires = data.get('nombre_exemplaires', livre.nombre_exemplaires)
        db.session.commit()
        return jsonify(livre.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/livres/<int:id>', methods=['DELETE'])
@login_required
def delete_livre(id):
    livre = Livre.query.filter_by(id_livre=id, id_utilisateur=current_user.id_utilisateur).first()
    if not livre:
        return jsonify({'error': 'Livre non trouvé'}), 404
    
    try:
        db.session.delete(livre)
        db.session.commit()
        return jsonify({'message': 'Livre supprimé'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============ MEMBRES ============

@app.route('/api/membres', methods=['GET'])
@login_required
def get_membres():
    membres = Membre.query.filter_by(id_utilisateur=current_user.id_utilisateur).all()
    return jsonify([membre.to_dict() for membre in membres])

@app.route('/api/membres', methods=['POST'])
@login_required
def create_membre():
    data = request.json
    try:
        nouveau_membre = Membre(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            telephone=data.get('telephone', ''),
            statut='actif',
            id_utilisateur=current_user.id_utilisateur
        )
        db.session.add(nouveau_membre)
        db.session.commit()
        return jsonify(nouveau_membre.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/membres/<int:id>', methods=['PUT'])
@login_required
def update_membre(id):
    membre = Membre.query.filter_by(id_membre=id, id_utilisateur=current_user.id_utilisateur).first()
    if not membre:
        return jsonify({'error': 'Membre non trouvé'}), 404
    
    data = request.json
    try:
        membre.nom = data.get('nom', membre.nom)
        membre.prenom = data.get('prenom', membre.prenom)
        membre.email = data.get('email', membre.email)
        membre.telephone = data.get('telephone', membre.telephone)
        membre.statut = data.get('statut', membre.statut)
        db.session.commit()
        return jsonify(membre.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/membres/<int:id>', methods=['DELETE'])
@login_required
def delete_membre(id):
    membre = Membre.query.filter_by(id_membre=id, id_utilisateur=current_user.id_utilisateur).first()
    if not membre:
        return jsonify({'error': 'Membre non trouvé'}), 404
    
    try:
        db.session.delete(membre)
        db.session.commit()
        return jsonify({'message': 'Membre supprimé'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============ EMPRUNTS ============

@app.route('/api/emprunts', methods=['GET'])
@login_required
def get_emprunts():
    emprunts = Emprunt.query.join(Livre).filter(Livre.id_utilisateur == current_user.id_utilisateur).all()
    return jsonify([emprunt.to_dict() for emprunt in emprunts])

@app.route('/api/emprunts', methods=['POST'])
@login_required
def create_emprunt():
    data = request.json
    
    livre = Livre.query.filter_by(id_livre=data['id_livre'], id_utilisateur=current_user.id_utilisateur).first()
    if not livre or livre.disponibles <= 0:
        return jsonify({'error': 'Livre non disponible'}), 400
    
    membre = Membre.query.filter_by(id_membre=data['id_membre'], id_utilisateur=current_user.id_utilisateur).first()
    if not membre or membre.statut != 'actif':
        return jsonify({'error': 'Membre invalide'}), 400
    
    try:
        nouvel_emprunt = Emprunt(
            id_livre=data['id_livre'],
            id_membre=data['id_membre'],
            date_retour_prevue=datetime.utcnow() + timedelta(days=14),
            statut='en_cours'
        )
        livre.disponibles -= 1
        db.session.add(nouvel_emprunt)
        db.session.commit()
        return jsonify(nouvel_emprunt.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/emprunts/<int:id>/retour', methods=['POST'])
@login_required
def retourner_livre(id):
    emprunt = Emprunt.query.join(Livre).filter(
        Emprunt.id_emprunt == id,
        Livre.id_utilisateur == current_user.id_utilisateur
    ).first()
    
    if not emprunt:
        return jsonify({'error': 'Emprunt non trouvé'}), 404
    
    try:
        emprunt.date_retour_reelle = datetime.utcnow()
        emprunt.statut = 'retourne'
        
        if emprunt.date_retour_reelle.date() > emprunt.date_retour_prevue:
            jours_retard = (emprunt.date_retour_reelle.date() - emprunt.date_retour_prevue).days
            amende = Amende(id_emprunt=emprunt.id_emprunt, montant=jours_retard * 0.50, statut='impayee')
            db.session.add(amende)
        
        livre = Livre.query.get(emprunt.id_livre)
        livre.disponibles += 1
        db.session.commit()
        return jsonify(emprunt.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============ AMENDES ============

@app.route('/api/amendes', methods=['GET'])
@login_required
def get_amendes():
    amendes = Amende.query.join(Emprunt).join(Livre).filter(Livre.id_utilisateur == current_user.id_utilisateur).all()
    return jsonify([amende.to_dict() for amende in amendes])

@app.route('/api/amendes/<int:id>/payer', methods=['POST'])
@login_required
def payer_amende(id):
    amende = Amende.query.join(Emprunt).join(Livre).filter(
        Amende.id_amende == id,
        Livre.id_utilisateur == current_user.id_utilisateur
    ).first()
    
    if not amende:
        return jsonify({'error': 'Amende non trouvée'}), 404
    
    try:
        amende.statut = 'payee'
        db.session.commit()
        return jsonify(amende.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============ STATS ============

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    return jsonify({
        'total_livres': Livre.query.filter_by(id_utilisateur=current_user.id_utilisateur).count(),
        'total_membres': Membre.query.filter_by(id_utilisateur=current_user.id_utilisateur).count(),
        'emprunts_actifs': Emprunt.query.join(Livre).filter(Livre.id_utilisateur == current_user.id_utilisateur, Emprunt.statut == 'en_cours').count(),
        'amendes_impayees': Amende.query.join(Emprunt).join(Livre).filter(Livre.id_utilisateur == current_user.id_utilisateur, Amende.statut == 'impayee').count()
    })

@app.route('/')
def home():
    return jsonify({'message': 'API BiblioTech', 'version': '2.0', 'auth': 'Flask-Login'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)