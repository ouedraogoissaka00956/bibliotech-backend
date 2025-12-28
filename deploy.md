# 🚀 Guide Complet : Déploiement BiblioTech sur Render avec PostgreSQL

---

## 📋 Prérequis

- [x] Compte GitHub
- [x] Compte Render.com (gratuit)
- [x] PostgreSQL configuré dans le code
- [x] Variables d'environnement prêtes

---

## 🐙 ÉTAPE 1 : Préparer et Pousser sur GitHub

### 1.1 Structure finale du projet

```
backend/
├── app.py
├── models.py
├── config.py
├── auto_backup.py
├── requirements.txt
├── .gitignore
├── README.md
└── uploads/
    └── .gitkeep
```

### 1.2 Vérifier .gitignore

Assurez-vous que ces fichiers sont exclus :

```gitignore
venv/
__pycache__/
*.pyc
.env
.env.local
instance/
*.db
*.sqlite
uploads/*
!uploads/.gitkeep
backups/
```

### 1.3 Initialiser Git

```bash
cd backend
git init
git add .
git commit -m "🚀 Initial commit - BiblioTech avec PostgreSQL"
```

### 1.4 Créer un repository GitHub

1. Allez sur https://github.com/new
2. **Nom** : `bibliotech-backend`
3. **Visibilité** : Private (recommandé)
4. **Ne pas** cocher "Initialize with README"
5. Cliquez sur **"Create repository"**

### 1.5 Pousser le code

```bash
git remote add origin https://github.com/VOTRE_USERNAME/bibliotech-backend.git
git branch -M main
git push -u origin main
```

---

## 🌐 ÉTAPE 2 : Créer la Base PostgreSQL sur Render

### 2.1 Créer un compte Render

1. Allez sur https://render.com
2. Cliquez sur **"Get Started"**
3. Connectez-vous avec **GitHub**

### 2.2 Créer une base PostgreSQL

1. Dans le dashboard, cliquez sur **"New +"**
2. Sélectionnez **"PostgreSQL"**

**Configuration** :
- **Name** : `bibliotech-db`
- **Database** : `bibliotech`
- **User** : `bibliotech`
- **Region** : `Frankfurt (EU Central)` ou proche de vous
- **PostgreSQL Version** : 16
- **Instance Type** : **Free**

3. Cliquez sur **"Create Database"**

⏳ **Attendez 2-3 minutes** que la base soit prête.

### 2.3 Récupérer l'URL de connexion

Une fois créée, vous verrez :
- **Internal Database URL** : Utilisez celle-ci (plus rapide)
- **External Database URL** : Pour connexion externe

📋 **Copiez l'Internal Database URL**, elle ressemble à :
```
postgres://bibliotech:XXX@dpg-XXX.frankfurt-postgres.render.com/bibliotech
```

---

## 🖥️ ÉTAPE 3 : Créer le Web Service

### 3.1 Nouveau Web Service

1. Cliquez sur **"New +"** → **"Web Service"**
2. Sélectionnez **"Build and deploy from a Git repository"**
3. Cliquez sur **"Connect account"** si nécessaire
4. Cherchez et sélectionnez votre repo **`bibliotech-backend`**

### 3.2 Configuration du service

**Settings de base** :
- **Name** : `bibliotech-backend`
- **Region** : `Frankfurt (EU Central)` (même que la DB)
- **Branch** : `main`
- **Root Directory** : (laisser vide)
- **Runtime** : `Python 3`
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `gunicorn app:app --bind 0.0.0.0:$PORT`

**Instance Type** :
- Sélectionnez **"Free"**

### 3.3 Variables d'environnement

Cliquez sur **"Advanced"** puis **"Add Environment Variable"** :

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Version Python |
| `FLASK_ENV` | `production` | Mode production |
| `SECRET_KEY` | [Générer ci-dessous](#générer-secret-key) | Clé secrète |
| `DATABASE_URL` | [URL copiée étape 2.3] | URL PostgreSQL |
| `SMTP_SERVER` | `smtp.gmail.com` | Serveur email |
| `SMTP_PORT` | `587` | Port SMTP |
| `SMTP_USERNAME` | `votre.email@gmail.com` | Votre email |
| `SMTP_PASSWORD` | `votre_mot_passe_app` | Mot de passe d'app |

#### <a name="générer-secret-key"></a>Générer SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copiez le résultat.

### 3.4 Créer le service

Cliquez sur **"Create Web Service"** → Le déploiement commence ! 🚀

⏳ **Attendez 5-10 minutes** pour le premier déploiement.

---

## ✅ ÉTAPE 4 : Vérifier le Déploiement

### 4.1 Voir les logs

Dans votre service, onglet **"Logs"** :

Vous devriez voir :
```
✅ Base de données initialisée!
📊 Utilisateurs enregistrés : 0
📚 Livres dans le catalogue : 0
👥 Membres actifs : 0
⏰ Sauvegarde automatique toutes les 30 minutes
🚀 Service de sauvegarde automatique démarré
```

### 4.2 Tester l'API

```bash
curl https://bibliotech-backend.onrender.com/
```

Réponse attendue :
```json
{
  "message": "API BiblioTech",
  "version": "2.0",
  "auth": "Flask-Login"
}
```

### 4.3 Votre backend est en ligne ! 🎉

URL : `https://bibliotech-backend.onrender.com`

---

## 🎨 ÉTAPE 5 : Déployer le Frontend

### 5.1 Mettre à jour l'URL de l'API

**Option A : Avec variable d'environnement (Recommandé)**

Créez `frontend/.env.production` :

```env
VITE_API_URL=https://bibliotech-backend.onrender.com/api
```

Modifiez `frontend/src/services/api.js` :

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export default axios.create({
  baseURL: API_URL,
  withCredentials: true
});
```

**Option B : Directement dans le code**

```javascript
const API_URL = import.meta.env.PROD 
  ? 'https://bibliotech-backend.onrender.com/api'
  : 'http://localhost:5000/api';
```

### 5.2 Déployer sur Vercel (GRATUIT)

```bash
cd frontend

# Installer Vercel CLI
npm install -g vercel

# Build
npm run build

# Déployer
vercel --prod
```

Suivez les instructions :
1. **Set up and deploy** : Oui
2. **Which scope** : Votre compte
3. **Link to existing project** : Non
4. **Project name** : `bibliotech-frontend`
5. **Directory** : `./`
6. **Override settings** : Non

### 5.3 Configurer CORS

Retournez dans Render, **Environment** :

Modifiez `CORS_ORIGINS` :
```
https://bibliotech-frontend.vercel.app,https://localhost:5173
```

**Cliquez sur "Save Changes"** → Le service redémarre automatiquement.

---

## 🎯 ÉTAPE 6 : Tester l'Application Complète

### 6.1 Aller sur votre frontend

```
https://bibliotech-frontend.vercel.app
```

### 6.2 Créer un compte

1. Cliquez sur **"S'inscrire"**
2. Remplissez le formulaire
3. **Vérifiez votre email** 📧
4. Cliquez sur le bouton dans l'email
5. Connectez-vous !

### 6.3 Tester toutes les fonctionnalités

- ✅ Inscription + Vérification email
- ✅ Connexion / Déconnexion
- ✅ Ajouter des livres
- ✅ Ajouter des membres
- ✅ Créer des emprunts
- ✅ Upload photo de profil

---

## 🔧 ÉTAPE 7 : Maintenance et Mises à Jour

### 7.1 Mettre à jour le code

```bash
# Modifier votre code localement
git add .
git commit -m "✨ Nouvelle fonctionnalité"
git push

# Render détecte automatiquement et redéploie !
```

### 7.2 Voir les logs

- **Render Dashboard** → Votre service → **"Logs"**
- En temps réel pendant le déploiement

### 7.3 Backup de la base de données

Render fait des backups automatiques, mais pour être sûr :

1. **Dashboard** → **bibliotech-db**
2. **Settings** → **Manual Snapshot**
3. Télécharger si nécessaire

---

## 💰 Coûts

| Service | Plan | Coût |
|---------|------|------|
| **Render Web Service** | Free | 0€/mois |
| **Render PostgreSQL** | Free | 0€/mois (1 GB) |
| **Vercel Frontend** | Hobby | 0€/mois |
| **Domain (optionnel)** | .com | ~10€/an |

**Total : GRATUIT** 🎉

### Limitations du plan gratuit :
- Web Service : Se met en veille après 15 min d'inactivité
- PostgreSQL : 1 GB de stockage, 100 heures/mois
- Premier chargement peut prendre 30-60 secondes

### Upgrade (si besoin) :
- **Starter Plan** : $7/mois → Pas de mise en veille
- **PostgreSQL Standard** : $7/mois → Plus de stockage

---

## 🎉 FÉLICITATIONS !

Votre application BiblioTech est maintenant en ligne ! 🚀

**URLs** :
- Backend : `https://bibliotech-backend.onrender.com`
- Frontend : `https://bibliotech-frontend.vercel.app`
- Base de données : PostgreSQL sur Render

**Prochaines étapes** :
- [ ] Acheter un nom de domaine personnalisé
- [ ] Configurer des alertes de monitoring
- [ ] Ajouter Google Analytics
- [ ] Optimiser les performances

---

## ❓ Problèmes Courants

### Le backend ne démarre pas
- Vérifiez les logs dans Render
- Assurez-vous que `DATABASE_URL` est correct
- Vérifiez `requirements.txt`

### Erreur CORS
- Ajoutez votre domaine frontend dans `CORS_ORIGINS`
- Format : `https://votre-site.vercel.app` (sans slash final)

### Email ne s'envoie pas
- Vérifiez `SMTP_USERNAME` et `SMTP_PASSWORD`
- Utilisez un mot de passe d'application Gmail

### Base de données vide après redémarrage
- Normal avec SQLite sur Render
- Avec PostgreSQL, les données persistent ! ✅

---

## 📞 Support

- **Render Docs** : https://render.com/docs
- **Vercel Docs** : https://vercel.com/docs
- **PostgreSQL Docs** : https://www.postgresql.org/docs/