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

---

## Fonctionnalités principales

### Portail public
- Page d'accueil avec bannières, blocs de services, actualités et sponsors
- Actualités nationales et internationales avec catégories et auteurs
- Bibliothèque de documents (PDF, Word, Excel, PowerPoint) avec téléchargement
- Médiathèque vidéo (YouTube, Vimeo ou upload direct) et galeries d'images
- Répertoire des ingénieurs et architectes
- Formulaire de contact

### Espace membre (authentifié)
- Tableau de bord personnel
- Gestion du profil et informations professionnelles
- Suivi des cotisations et justificatifs de paiement
- Téléchargement du certificat professionnel avec QR code
- Opportunités : offres d'emploi, appels d'offres, collaborations
- Forum de discussion entre membres

### Administration
- Gestion des demandes d'adhésion avec pièces justificatives
- Système de plaintes avec numéro de référence auto-généré et suivi de statut
- Structure de gouvernance : Conseil d'Administration, Commission d'Audit, Conseil de Discipline (par année)
- Gestion des publicités et sponsors avec plages de dates et positionnement
- Normes et standards professionnels
- Formations continues avec contenus multimédias

---

## Structure du projet

```
cniah_project/
├── src/
│   ├── apps/
│   │   ├── core/           # Pages, documents, gouvernance, adhésion
│   │   ├── members/        # Authentification et tableau de bord membre
│   │   ├── news/           # Actualités
│   │   ├── advertisements/ # Sponsors et publicités
│   │   └── contact/        # Formulaires de contact
│   ├── config/             # Settings Django et routing URL
│   ├── templates/          # Templates HTML
│   ├── static/             # CSS, JS, images
│   └── media/              # Fichiers uploadés
├── Dockerfile
├── docker-compose.yml
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
git clone <url-du-depot>
cd cniah_project

# Configurer les variables d'environnement
cp .env.example .env  # puis éditer .env selon votre environnement

# Démarrer les services
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
```

---

## Commandes utiles

```bash
# Créer de nouvelles migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Ouvrir un shell Django
python manage.py shell

# Vider et recréer les données statiques
python manage.py collectstatic --clear --noinput
```

---

## Informations du projet

- **Langue** : Français
- **Fuseau horaire** : America/Port-au-Prince (Haïti)
- **Version Django** : 5.0
- **Version Python** : 3.11
