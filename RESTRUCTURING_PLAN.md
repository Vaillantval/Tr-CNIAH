# Plan de restructuration — CNIAH

> Rédigé le 2026-04-21 — basé sur un audit complet du code source.

## Vue d'ensemble

L'audit révèle un projet **fonctionnel mais fragilisé** par 4 grandes catégories de problèmes : sécurité, qualité du code, architecture, et absence de tests. Le plan est organisé en 4 phases séquentielles, chacune livrable de façon indépendante.

---

## Phase 1 — Sécurité critique

### 1.1 Créer des `forms.py` dans chaque app

Actuellement, toutes les vues accèdent à `request.POST` directement sans validation. Il faut créer des formulaires Django dans les 5 apps :

| App | Formulaires à créer |
|-----|---------------------|
| `core` | `AdhesionForm`, `PlainteForm`, `NewsletterForm` |
| `members` | `InscriptionForm`, `ConnexionForm`, `ProfilForm`, `NouveauSujetForm` |
| `contact` | `ContactForm` |
| `news` | *(lecture seule, géré par l'admin)* |
| `advertisements` | *(géré par l'admin)* |

### 1.2 Validation des fichiers uploadés

Les vues `adhesion_view`, `deposer_plainte` et `mes_cotisations` acceptent n'importe quel fichier sans contrôle. Créer un validateur central dans `src/apps/core/validators.py` :

- Types autorisés : PDF, JPG, PNG, DOCX
- Taille maximale : définie dans `settings.py` (le paramètre existe déjà mais n'est jamais appliqué dans les vues)

### 1.3 Protection des vues membres

Vues sans `@login_required` à corriger :

- `src/apps/core/views.py` — `MembersDashboardView` (ligne ~107)
- `src/apps/members/views.py` — filtrage des données par `request.user` absent sur toutes les vues (cotisations, documents, forum) : un membre peut potentiellement accéder aux données d'un autre en manipulant l'URL

### 1.4 Fusionner les modèles `Sponsor` en double

Deux modèles `Sponsor` identiques coexistent :

- `src/apps/advertisements/models.py` lignes 6-22 — **à supprimer**
- `src/apps/core/models.py` lignes 805-828 — **à conserver**

Créer une migration de consolidation et mettre à jour toutes les références dans les vues et l'admin.

### 1.5 Compléter la configuration des variables d'environnement

Valeurs actuellement hardcodées à déplacer dans `.env` :

| Variable | Emplacement actuel |
|----------|--------------------|
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | `settings.py` lignes 250-256 |
| `SITE_URL` | `settings.py` ligne 259 (vaut `localhost:8002`) |

Créer un fichier `.env.example` documenté pour faciliter les déploiements futurs.

---

## Phase 2 — Qualité du code

### 2.1 Transactions base de données

`deposer_plainte` crée une `Plainte` puis des `DocumentPlainte` dans une boucle sans transaction atomique. Si un fichier échoue, la plainte est sauvegardée sans ses pièces jointes. Corriger en enveloppant dans `@transaction.atomic`.

Même problème potentiel dans `adhesion_view` (8 uploads séquentiels sans transaction).

### 2.2 Optimisation des requêtes (problèmes N+1)

| Vue | Problème | Correction |
|-----|----------|------------|
| `about()` | Boucle sur membres de chaque comité sans prefetch | `prefetch_related('membres')` |
| `HomeView` | 4+ requêtes séparées sans jointures | `select_related` sur les relations clés |
| `membres_actifs()` | Pas de `select_related` sur le titre professionnel | `select_related('titre')` |

### 2.3 Corriger les `related_name` en conflit

Dans `src/apps/core/models.py` : `VideoResource` et `ImageGallery` utilisent tous les deux `related_name='images'` sur `DocumentCategory`. Ce conflit provoque une erreur Django au démarrage ou des comportements imprévisibles.

### 2.4 Corriger la newsletter

Dans `src/apps/core/views.py` ligne ~118 : la sauvegarde en base est commentée. L'abonnement à la newsletter ne fait rien actuellement.

### 2.5 Centraliser les valeurs hardcodées

Créer `src/apps/core/constants.py` pour regrouper :

- La chaîne `'ZAFE GOUDOUGOUDOU'` (utilisée comme filtre dans `DocumentsView`)
- `'Liste des comptes bancaires'` (filtre dans `cotisation()`)
- Adresse et téléphone du CNIAH dans les PDF générés (`generer_certificat_pdf()`)

### 2.6 Ajouter du logging

Configurer le logging Python dans `settings.py` et ajouter des appels `logger.error()` / `logger.info()` dans les vues critiques :

- Authentification (connexion réussie/échouée)
- Soumission de plainte
- Génération de certificat PDF
- Téléchargements de documents

### 2.7 Supprimer le code mort

| Élément | Raison |
|---------|--------|
| `src/apps/core/signals.py` | Jamais importé ni connecté |
| `mptt` dans `requirements.txt` | Installé mais jamais utilisé dans le code |
| Doublons dans `requirements.txt` | `psycopg2` et `python-decouple` listés deux fois |

---

## Phase 3 — Architecture

### 3.1 Alléger l'app `core`

`src/apps/core/models.py` fait 929 lignes et mélange des domaines sans rapport. Découper en apps Django séparées :

```
core/          →  Banner, ServiceBlock, Proposition (configuration page d'accueil)
documents/     →  ReferenceDocument, VideoResource, ImageGallery, DocumentCategory
governance/    →  ConseilAdmin, CommissionAudit, ConseilDiscipline, Norme
compliance/    →  Plainte, DemandeAdhesion, Certification
```

> **Attention** : cette étape est la plus risquée. Elle doit être réalisée **après** que les tests de Phase 4 sont en place pour servir de filet de sécurité.

### 3.2 Système de permissions

Aucun groupe ou permission Django n'est défini. Créer :

| Groupe | Accès |
|--------|-------|
| `Membre` | Espace membre, dashboard, cotisations, forum |
| `Modérateur` | Gestion forum, suivi des plaintes |
| `Administrateur` | Accès complet à l'admin |

Ajouter `@permission_required` sur les vues qui le nécessitent.

### 3.3 Compléter le flux de vérification d'email

Le modèle `User` possède un champ `email_verified` et un token de vérification, mais `inscription()` n'envoie jamais d'email et ne valide rien. Implémenter :

1. Envoi d'un email de confirmation à l'inscription
2. Vue de confirmation : `/membres/verify/<token>/`
3. Blocage de connexion si `email_verified=False`

### 3.4 Réinitialisation de mot de passe

Utiliser les vues Django built-in (`PasswordResetView`, `PasswordResetConfirmView`) — aucune URL de reset n'est câblée actuellement.

### 3.5 Limiter le taux de requêtes (rate limiting)

- Ajouter un rate limit sur la vue de connexion (protection brute-force)
- Protéger la soumission de plainte (endpoint non authentifié avec upload de fichiers)
- Utiliser `django-ratelimit` ou le middleware cache Django

---

## Phase 4 — Tests

### Structure cible

```
src/apps/core/tests/
├── test_models.py        # Validation des modèles, __str__, contraintes DB
├── test_views.py         # Status codes, redirections, permissions
├── test_forms.py         # Validation des formulaires, cas limites
└── test_integration.py   # Flux complets (adhésion, plainte, connexion)

src/apps/members/tests/
├── test_auth.py          # Inscription, connexion, déconnexion, vérification email
├── test_dashboard.py     # Accès membre, cotisations, génération certificat PDF
└── test_forum.py         # Création sujet, messages, accès refusé

src/apps/news/tests/
└── test_views.py         # Liste, détail, filtres par catégorie et type

src/apps/contact/tests/
└── test_contact.py       # Soumission formulaire, sauvegarde en base

src/apps/advertisements/tests/
└── test_ads.py           # Affichage par position, filtrage par dates actives
```

### Cas de test prioritaires

| Catégorie | Scénarios à couvrir |
|-----------|---------------------|
| **Authentification** | Inscription valide/invalide, connexion, déconnexion, accès refusé sans login |
| **Adhésion** | Soumission complète, champs manquants, types de fichiers invalides |
| **Plainte** | Transaction atomique, référence auto-générée, pièces jointes multiples |
| **Certificat** | Génération PDF, QR code intégré, accès membre uniquement |
| **Forum** | Création sujet, réponse, accès refusé aux non-membres |
| **Newsletter** | Soumission valide, rejet d'email en double |
| **Permissions** | Chaque vue protégée redirige un utilisateur anonyme vers la page de login |
| **Sécurité fichiers** | Rejet d'un fichier trop lourd, rejet d'une extension interdite |

### Outils recommandés

```
pytest-django     # Runner de tests adapté à Django
factory-boy       # Génération de données de test (factories pour chaque modèle)
coverage          # Rapport de couverture de code
```

Ajouter dans `requirements.txt` (section dev) :

```
pytest-django>=4.8
factory-boy>=3.3
coverage>=7.4
```

### Objectif de couverture

| Étape | Cible |
|-------|-------|
| Phase 4a — modèles | 100% des modèles testés |
| Phase 4b — vues | Toutes les vues avec `TestClient` |
| Phase 4c — intégration | Flux end-to-end complets |
| **Cible finale** | **≥ 80% de couverture globale** |

---

## Séquençage recommandé

```
Semaine 1  →  Phase 1 (sécurité) + Phase 4a (tests des modèles)
Semaine 2  →  Phase 2 (qualité du code) + Phase 4b (tests des vues)
Semaine 3  →  Phase 3.2 à 3.5 (permissions, email, rate limiting) + Phase 4c (intégration)
Semaine 4  →  Phase 3.1 (découpage de core) — uniquement avec les tests en place
```

> Le découpage de `core` est volontairement reporté à la dernière semaine : c'est le changement le plus risqué structurellement, et les tests rédigés aux semaines précédentes servent de filet de sécurité pour valider que rien ne régresse.

---

## Par où commencer

**Recommandation : Phase 1.1 — créer les `forms.py`.**

C'est la fondation de tout le reste : la validation des formulaires conditionne la sécurité, la qualité du code, et la testabilité. Une fois les formulaires en place, les phases suivantes s'enchaînent naturellement.
