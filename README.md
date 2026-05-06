# CNIAH — Conseil National des Ingénieurs et Architectes d'Haïti

Site web officiel du CNIAH : portail institutionnel, gestion des membres, actualités et services aux professionnels.

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Django 5.0 / Python 3.11 |
| Base de données | PostgreSQL 15 |
| Éditeur rich text | django-ckeditor |
| Interface admin | django-jazzmin |
| Fichiers statiques | WhiteNoise |
| Conteneurisation | Docker + Docker Compose |
| Serveur WSGI | Gunicorn |
| Tâches asynchrones | Celery + Redis |
| Protection brute-force | django-axes |
| Audit logs | django-simple-history |
| PDF & QR codes | ReportLab + qrcode |

---

## Fonctionnalités principales

### Portail public
- Page d'accueil avec bannières, blocs de services, actualités et sponsors
- Actualités nationales et internationales avec catégories, auteurs et **recherche full-text PostgreSQL**
- Bibliothèque de documents (PDF, Word, Excel, PowerPoint) avec téléchargement
- Médiathèque vidéo (YouTube, Vimeo ou upload direct) et galeries d'images
- Répertoire des ingénieurs et architectes
- Formulaire de contact

### Espace membre (authentifié)
- Tableau de bord personnel
- Gestion du profil et informations professionnelles
- Suivi des cotisations et justificatifs de paiement
- Téléchargement du certificat professionnel avec **QR code généré et stocké**
- Opportunités : offres d'emploi, appels d'offres, collaborations
- Forum de discussion entre membres

### Administration
- Gestion des demandes d'adhésion avec pièces justificatives
- Système de plaintes avec numéro de référence auto-généré et suivi de statut
- Structure de gouvernance : Conseil d'Administration, Commission d'Audit, Conseil de Discipline (par année)
- Gestion des publicités et sponsors avec plages de dates et positionnement
- Normes et standards professionnels
- Formations continues avec contenus multimédias
- **Historique complet des modifications** sur les modèles sensibles (Membre, Plainte, Certification, Adhésion)

---

## Structure du projet

```
cniah_project/
├── src/
│   ├── apps/
│   │   ├── core/           # Pages, documents, gouvernance, adhésion, certifications
│   │   ├── members/        # Authentification, tableau de bord, tasks Celery
│   │   ├── news/           # Actualités avec recherche full-text
│   │   ├── advertisements/ # Publicités avec gestion des dates
│   │   └── contact/        # Formulaires de contact
│   ├── config/             # Settings Django, routing URL, configuration Celery
│   ├── templates/          # Templates HTML (Tailwind CSS)
│   ├── static/             # CSS, JS, images
│   └── media/              # Fichiers uploadés
├── Dockerfile
├── docker-compose.yml      # Services : db, web, redis, worker, adminer
├── requirements.txt
└── .env
```

---

## Démarrage rapide

### Prérequis
- [Docker](https://www.docker.com/) et Docker Compose

### Lancement avec Docker (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/Vaillantval/Tr-CNIAH.git
cd Tr-CNIAH

# Configurer les variables d'environnement
cp .env.example .env  # puis éditer .env selon votre environnement

# Démarrer tous les services (web + db + redis + worker)
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Application web | http://localhost:8002 |
| Administration Django | http://localhost:8002/admin/ |
| Adminer (base de données) | http://localhost:8081 |

### Lancement en développement local

```bash
cd src

# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r ../requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Lancer le serveur
python manage.py runserver
```

Pour démarrer le worker Celery (emails asynchrones) en développement :

```bash
celery -A config worker -l info
```

---

## Configuration

Créer un fichier `.env` à la racine du projet :

```env
DEBUG=1
SECRET_KEY=votre-cle-secrete
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=cniah_db
POSTGRES_USER=cniah_user
POSTGRES_PASSWORD=cniah_password
DATABASE_URL=postgresql://cniah_user:cniah_password@db:5432/cniah_db

# Celery / Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email (console en dev, SMTP en prod)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@cniah.ht

# URL publique du site (utilisée pour les QR codes et liens email)
SITE_URL=http://localhost:8002
```

---

## Commandes utiles

```bash
# Appliquer les migrations
python manage.py migrate

# Régénérer les QR codes manquants sur les certifications existantes
python manage.py regenerate_qrcodes

# Créer de nouvelles migrations
python manage.py makemigrations

# Ouvrir un shell Django
python manage.py shell

# Collecter les fichiers statiques
python manage.py collectstatic --clear --noinput

# Lancer les tests avec rapport de couverture
pytest --cov=apps --cov-report=term-missing
```

---

## Sécurité

- **HTTPS/HSTS** activés automatiquement en production (`DEBUG=0`)
- **Protection brute-force** : blocage IP après 5 tentatives de connexion échouées (django-axes)
- **Validation MIME** : les fichiers uploadés sont vérifiés par magic bytes, pas seulement par extension
- **Cookies sécurisés** : `SESSION_COOKIE_SECURE` et `CSRF_COOKIE_SECURE` en production
- **Audit logs** : historique complet des modifications sur Membre, Plainte, Certification, DemandeAdhésion

---

## Tests

```bash
# Lancer tous les tests
pytest

# Avec rapport de couverture
pytest --cov=apps --cov-report=term-missing

# Une app spécifique
pytest apps/news/
```

Couverture actuelle : ~40% (news, advertisements, members auth/dashboard/forum, core views).

---

## Informations du projet

- **Langue** : Français
- **Fuseau horaire** : America/Port-au-Prince (Haïti)
- **Version Django** : 5.0
- **Version Python** : 3.11
- **Dépôt** : https://github.com/Vaillantval/Tr-CNIAH
