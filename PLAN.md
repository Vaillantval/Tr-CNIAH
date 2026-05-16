# Plan d'implémentation — CNIAH v2

> Réunion client du 16 mai 2026  
> Statut : **En attente d'approbation**

---

## Vue d'ensemble

Ce plan couvre 11 fonctionnalités distinctes issues des retours clients, organisées par priorité et dépendances. Chaque section décrit le quoi, le comment, les choix techniques retenus et les migrations nécessaires.

---

## F1 — Email fonctionnel

### Contexte
L'email est actuellement en mode `console.EmailBackend` en dev, et le backend SMTP pointe vers Gmail (configuration non fonctionnelle sans mot de passe d'application). En production, il faut un service d'envoi fiable.

### Service retenu : **Resend** (gratuit au démarrage)
- **3 000 emails/mois** gratuits, 100/jour
- Compatible SMTP (aucun changement de code, juste les variables d'env)
- Excellente délivrabilité, supporte les domaines personnalisés (cniah.ht)
- Alternative si Resend est bloqué : **Brevo** (300 emails/jour gratuit, SMTP identique)

### Configuration SMTP Resend
```
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=465 (SSL) ou 587 (TLS)
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=<API_KEY_RESEND>
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=noreply@cniah.ht
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Cas d'utilisation email — inventaire complet

| Cas | Tâche Celery | Statut |
|-----|-------------|--------|
| Vérification email à l'inscription | `envoyer_email_verification` | ✅ Existe |
| Email de bienvenue après vérification | `envoyer_email_bienvenue` | ✅ Existe |
| Confirmation de demande d'adhésion | `envoyer_confirmation_adhesion` | ✅ Existe |
| Décision sur demande d'adhésion | `notifier_statut_demande_adhesion` | ✅ Existe |
| Changement de statut d'une plainte | `notifier_changement_statut_plainte` | ✅ Existe |
| Validation d'une cotisation | `notifier_cotisation_validee` | ✅ Existe |
| Rappel cotisation expirée | `envoyer_rappel_cotisation` | ✅ Existe |
| Notification admin — nouvelle adhésion | `notifier_admin_nouvelle_adhesion` | ✅ Existe |
| Notification admin — nouvelle plainte | `notifier_admin_nouvelle_plainte` | ✅ Existe |
| Notification admin — preuve de paiement | `notifier_admin_preuve_cotisation` | ✅ Existe |
| **Réinitialisation de mot de passe** | Django built-in `password_reset` | ⚠️ À vérifier/activer |
| **Envoi du certificat PDF par email** | `envoyer_certificat_par_email` | 🆕 À créer |
| **Rappel renouvellement certificat** | `rappel_renouvellement_certificat` | 🆕 À créer |
| **Confirmation paiement certificat** | `confirmer_paiement_certificat` | 🆕 À créer |
| **Confirmation d'un don reçu** | `confirmer_reception_don` | 🆕 À créer |

### Travaux
1. Ajouter `RESEND_` vars dans `.env.example` et documenter la procédure
2. Vérifier que les URLs Django password-reset sont connectées et les templates existent
3. Créer les 4 nouvelles tâches Celery listées ci-dessus
4. Tester chaque cas en dev avec `django.core.mail.backends.locmem.EmailBackend`

---

## F2 — Miniatures YouTube

### Diagnostic
Le modèle `VideoResource.get_thumbnail_url()` génère correctement `https://img.youtube.com/vi/{id}/hqdefault.jpg`. Le problème est dans le template : les balises `<img>` utilisent probablement la méthode `get_embed_url()` au lieu de `get_thumbnail_url()`, ou le rendu se fait dans un contexte bloqué par CSP.

### Travaux
1. Auditer le template `video_list.html` / `video_detail.html` pour repérer comment la miniature est affichée
2. S'assurer que `get_thumbnail_url()` est appelé (et non l'URL embed)
3. Corriger la directive CSP (`img-src`) si nécessaire dans le middleware de sécurité

---

## F3 — Masquer les montants au public

### Règle
Les montants financiers (cotisations, paiements certificat, dons) ne doivent être visibles que par les membres connectés, dans leur espace personnel.

### Travaux
1. Auditer tous les templates publics pour toute référence à `montant`, `amount`, `prix`
2. Supprimer ou entourer avec `{% if user.is_authenticated and user.membre_actif %}` les affichages de montants
3. Ne rien changer dans les templates de l'espace membres (déjà protégé par `@login_required`)
4. Vérifier les vues publiques (membres actifs, adhesion, home) — aucun montant ne doit fuiter

---

## F4 — Affichage email et téléphone des membres

### Contexte
`MembreActif` n'a pas de champs email/téléphone propres. Ces données sont sur le modèle `User` (`email`, `phone`). Certains membres actifs n'ont pas de compte utilisateur.

### Choix technique
Ajouter deux champs optionnels directement sur `MembreActif` :
- `email_public` (`EmailField`, optionnel)
- `telephone_public` (`CharField`, optionnel)

Ces champs sont remplis manuellement par l'admin et affichés sur la liste publique si non vides.

### Travaux
1. Migration pour ajouter `email_public` et `telephone_public` sur `MembreActif`
2. Mettre à jour le template de liste des membres actifs pour afficher ces champs si renseignés
3. Mettre à jour l'admin pour permettre la saisie

---

## F5 — Certificat : numéro, design, PDF, signature, envoi email

### 5.1 — Numéro sur le certificat
Le champ `numero_certificat` existe. Il suffit de l'afficher dans le template/PDF.

### 5.2 — Design de vrai certificat

**Librairie retenue : WeasyPrint**
- Permet de générer un PDF depuis un template HTML/CSS
- Supporte les images (signature, logo, arrière-plan décoratif)
- Supérieur à reportlab pour les mises en page complexes
- À ajouter dans `requirements.txt`

**Modèle singleton : `ConfigurationCertificat`**
```python
class ConfigurationCertificat(models.Model):
    nom_president = models.CharField(max_length=100)
    titre_president = models.CharField(max_length=100, default="Président du CNIAH")
    signature_president = models.ImageField(upload_to='config/signatures/')
    logo_organisation = models.ImageField(upload_to='config/', blank=True)
    texte_bas_page = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Configuration Certificat"
```

Le client fournira le fichier de signature — l'admin l'uploade dans ce modèle.

### 5.3 — Template HTML du certificat (en français)
Un template `certificate_template.html` avec :
- En-tête : Logo CNIAH + nom de l'organisation
- Corps : « Le CNIAH certifie que M./Mme **[Nom]** ... » (texte officiel en français)
- Numéro de certificat bien visible
- QR code intégré
- Pied de page : signature du Président + date + sceau (optionnel)
- Design sobre et professionnel (couleurs CNIAH, bordure décorative)

### 5.4 — Génération PDF
Vue `telecharger_certificat_pdf(request, pk)` :
- Charge le certificat + configuration
- Rend le template HTML
- WeasyPrint → bytes PDF
- Retourne `HttpResponse` avec `Content-Type: application/pdf`

### 5.5 — Envoi par email
Nouvelle tâche Celery `envoyer_certificat_par_email(certification_id)` :
- Génère le PDF en mémoire
- Attache le PDF à un email
- Envoie au `user.email` du membre

### Travaux
1. Ajouter `weasyprint` dans `requirements.txt`
2. Créer `ConfigurationCertificat` (modèle singleton + admin)
3. Créer le template HTML du certificat
4. Créer la vue de téléchargement PDF
5. Créer la tâche Celery d'envoi par email
6. Ajouter bouton « Télécharger PDF » et « Recevoir par email » dans le dashboard membre

---

## F6 — Plaintes : accusé dans la liste des membres + type

### Contexte
- `membre_concerne` est un `CharField` (texte libre) — à transformer en sélection dans la liste des membres actifs
- `type_plainte` existe déjà dans le modèle et le formulaire ✅

### Choix technique
Remplacer `membre_concerne` par :
```python
membre_accuse = models.ForeignKey(
    MembreActif,
    on_delete=models.SET_NULL,
    null=True,
    related_name='plaintes_deposees_contre'
)
```
Garder l'ancien champ `membre_concerne` comme `CharField(blank=True)` pour la compatibilité avec les anciennes plaintes.

### Travaux
1. Migration : ajouter `membre_accuse` (FK vers MembreActif)
2. Mettre à jour `PlainteForm` : remplacer le champ texte par un `ModelChoiceField` filtré sur membres actifs
3. Template : utiliser un `<select>` avec recherche (select2 ou filtre natif)
4. Conserver l'affichage de `membre_concerne` dans l'admin pour les anciennes plaintes

---

## F7 — Carrousel de publicités

### Choix technique
Utiliser **Swiper.js** (via CDN ou npm) — léger, tactile, accessible.  
Alternative : Bootstrap Carousel si Bootstrap est déjà utilisé dans le projet.

### Travaux
1. Identifier les templates qui affichent les pubs (homepage banner + sidebar)
2. Remplacer le rendu statique par un carrousel Swiper
3. Configuration : autoplay, pagination, navigation arrows, responsive breakpoints
4. Conserver le tracking des clics

---

## F8 — Règles de renouvellement des certifications

### Règles métier
- **Date fixe de renouvellement** : le **30 septembre** de chaque année
- **Expiration** : premier 30 septembre **suivant** la date de délivrance
  - Exemple : certificat délivré le 15 mars 2026 → expire le 30 septembre 2026
  - Certificat délivré le 1er octobre 2026 → expire le 30 septembre 2027
- **Multi-année** : un admin peut créer un certificat valable N années (N × tarif annuel payé)
  - Expiration = 30 septembre de l'année de délivrance + N ans

### Modifications du modèle `Certification`
```python
annees_validite = models.PositiveIntegerField(default=1)  # 1, 2, 3...

@staticmethod
def calculer_expiration(date_delivrance: date, annees: int = 1) -> date:
    """Retourne le 30 septembre après N ans de validité."""
    annee_base = date_delivrance.year
    if date_delivrance > date(annee_base, 9, 30):
        annee_base += 1
    annee_expiration = annee_base + (annees - 1)
    return date(annee_expiration, 9, 30)
```

### Travaux
1. Migration : ajouter `annees_validite` sur `Certification`
2. Surcharger `save()` pour calculer automatiquement `date_expiration` via la méthode statique
3. Mettre à jour l'admin : afficher `annees_validite` et désactiver la saisie manuelle de `date_expiration`
4. Créer une tâche Celery périodique `verifier_expirations_certifications` (quotidienne) qui passe les certificats expirés en statut `'expire'`
5. Ajouter la tâche `rappel_renouvellement_certificat` (30 jours avant expiration)

---

## F9 — Séparation des espaces de paiement

### Contexte actuel
Un seul modèle `Cotisation` gère tout.

### Nouvelle architecture

#### Modèle 1 : `Cotisation` (cotisations annuelles/volontaires — inchangé)
Renommage conceptuel : cotisations de membre = contributions dues annuellement.

#### Modèle 2 : `PaiementCertificat` (nouveau)
```python
class PaiementCertificat(models.Model):
    user = models.ForeignKey(User, ...)
    certification = models.ForeignKey(Certification, null=True, blank=True, ...)
    montant = models.DecimalField(...)
    devise = models.CharField(...)
    annees_payees = models.PositiveIntegerField(default=1)
    statut = [en_attente, paye, refuse]
    methode_paiement = [moncash, natcash, virement, cash]
    reference_paiement = ...
    reference_plopplop = ...
    preuve_paiement = ...
    date_paiement = ...
```

#### Modèle 3 : `Don` (nouveau)
```python
class Don(models.Model):
    # Peut être fait par un membre connecté ou un visiteur anonyme
    user = models.ForeignKey(User, null=True, blank=True, ...)
    nom_donateur = models.CharField(max_length=100, blank=True)
    email_donateur = models.EmailField(blank=True)
    montant = models.DecimalField(...)
    devise = ...
    message = models.TextField(blank=True)
    statut = [recu, confirme]
    methode_paiement = ...
    reference_paiement = ...
    date_don = models.DateTimeField(auto_now_add=True)
```

### Dashboard membre — 3 sections distinctes
1. **Mes cotisations** — tableau des cotisations annuelles
2. **Mon certificat / Paiement de certification** — statut + historique des paiements certificat
3. **Mes dons** — historique des dons

### Travaux
1. Créer `PaiementCertificat` et `Don` dans `members/models.py`
2. Migrations
3. Vues et templates pour chaque section
4. Mise à jour des URLs membres
5. Admin pour les deux nouveaux modèles
6. Services Plopplop réutilisés pour les nouveaux paiements

---

## F10 — Tests

### Couverture cible pour les nouvelles fonctionnalités

| Fonctionnalité | Fichier de test | Tests à ajouter |
|----------------|----------------|-----------------|
| F1 — Emails | `members/tests/test_emails.py` | Envoi certificat, rappel renouvellement, confirmation don |
| F2 — Thumbnails YouTube | `core/tests/test_models.py` | `get_thumbnail_url()` pour différents formats d'URL YouTube |
| F3 — Masquage montants | `core/tests/test_views.py` | Pages publiques ne contiennent pas de montants |
| F4 — Contact membres | `core/tests/test_models.py` | Champs email/tel optionnels, affichage conditionnel |
| F5 — Certificat PDF | `core/tests/test_views.py` | Génération PDF, contenu, accès authentifié seulement |
| F6 — Plainte avec membre | `core/tests/test_forms.py` | Sélection FK valide, membre actif seulement |
| F7 — Carrousel | `advertisements/tests/test_views.py` | Pubs actives dans le contexte de la homepage |
| F8 — Dates certificat | `core/tests/test_models.py` | Logique expiration Sept 30, multi-année |
| F9 — Paiement séparé | `members/tests/test_payments.py` | CRUD PaiementCertificat, Don, séparation |

### Stratégie
- Utiliser `pytest-django` + `factory-boy` (déjà en place)
- `django.test.override_settings(CELERY_TASK_ALWAYS_EAGER=True)` pour les tests email
- `django.test.override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')` pour capturer les emails

---

## F11 — Liens sociaux dans le footer

Le client fournira les URLs. Un modèle de configuration `ConfigurationSite` (ou ajout à un modèle existant) stockera :
- Facebook, LinkedIn, Twitter/X, Instagram, YouTube, WhatsApp

Affichés dans le template `base.html` footer.

**À faire après réception des liens.**

---

## Résumé des besoins techniques

### Nouvelles dépendances Python
| Package | Usage |
|---------|-------|
| `weasyprint` | Génération PDF de haute qualité (certificats) |

*(Toutes les autres dépendances sont déjà présentes : celery, redis, reportlab, qrcode, Pillow)*

### Nouvelles migrations Django
1. `MembreActif` : +`email_public`, +`telephone_public`
2. `Plainte` : +`membre_accuse` (FK)
3. `Certification` : +`annees_validite`, logique `date_expiration` auto
4. `members` : nouveaux modèles `PaiementCertificat`, `Don`
5. `core` : nouveau modèle `ConfigurationCertificat`
6. Optionnel : `ConfigurationSite` pour les liens sociaux

### Variables d'environnement à ajouter
```
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=<RESEND_API_KEY>
EMAIL_USE_TLS=1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Fichier à recevoir du client
- Fichier image de la signature du Président (PNG transparent recommandé)
- URLs des réseaux sociaux pour le footer

---

## Ordre d'implémentation recommandé

1. **F2** — Miniatures YouTube (correction rapide, pas de migration)
2. **F3** — Masquage des montants (sécurité, pas de migration)
3. **F1** — Configuration email + nouveaux cas (fondation pour F5/F9)
4. **F4** — Contact membres (migration simple)
5. **F6** — Plaintes avec liste membres (migration + form)
6. **F8** — Règles certification (migration + logique métier)
7. **F9** — Séparation paiements (migrations + vues)
8. **F5** — Certificat PDF + design + envoi email (dépend F8)
9. **F7** — Carrousel publicités (frontend pur)
10. **F10** — Tests (en parallèle ou à la fin)
11. **F11** — Liens sociaux (après réception des URLs)

---

*Plan rédigé le 2026-05-16. Toute modification majeure de périmètre sera documentée ici.*
