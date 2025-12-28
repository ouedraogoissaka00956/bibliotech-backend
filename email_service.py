import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    """Service d'envoi d'emails pour BiblioTech"""
    
    @staticmethod
    def send_email(to_email, subject, html_content):
        """
        Envoie un email
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
        
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Configuration SMTP (Gmail exemple - adaptez selon votre fournisseur)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME')  # Votre email
            smtp_password = os.getenv('SMTP_PASSWORD')  # Mot de passe d'application
            from_email = os.getenv('FROM_EMAIL', smtp_username)
            
            # Créer le message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"BiblioTech <{from_email}>"
            message['To'] = to_email
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Connexion et envoi
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Sécuriser la connexion
                server.login(smtp_username, smtp_password)
                server.send_message(message)
            
            print(f" Email envoyé à {to_email}")
            return True
            
        except Exception as e:
            print(f" Erreur lors de l'envoi de l'email: {str(e)}")
            return False
    
    @staticmethod
    def send_reset_code(email, code, user_name):
        """
        Envoie le code de réinitialisation par email
        
        Args:
            email: Email de l'utilisateur
            code: Code à 6 chiffres
            user_name: Nom de l'utilisateur
        """
        subject = " Code de réinitialisation - BiblioTech"
        
        html_content = f"""
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
                        <div class="code">{code}</div>
                    </div>
                    
                    <div class="expiry">
                         Ce code expire dans 15 minutes
                    </div>
                    
                    <div class="warning">
                        <div class="warning-text">
                            <strong> Important :</strong><br>
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
        
        return EmailService.send_email(email, subject, html_content)