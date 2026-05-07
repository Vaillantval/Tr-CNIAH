# src/apps/members/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from apps.core.models import MembreActif

class User(AbstractUser):
    """Utilisateur personnalisé lié aux membres actifs"""
    membre_actif = models.OneToOneField(
        MembreActif,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_account'
    )
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = "Utilisateur Membre"
        verbose_name_plural = "Utilisateurs Membres"
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    @property
    def has_valid_certification(self):
        """Vérifie si le membre a une certification valide"""
        if not self.membre_actif:
            return False
        cert = self.membre_actif.certifications.filter(
            statut='valide',
            date_expiration__gte=timezone.now().date()
        ).first()
        return cert is not None
    
    @property
    def latest_certification(self):
        """Retourne la certification la plus récente"""
        if not self.membre_actif:
            return None
        return self.membre_actif.certifications.filter(
            statut='valide'
        ).order_by('-date_delivrance').first()


class Cotisation(models.Model):
    """Cotisations des membres"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('expiree', 'Expirée'),
    ]
    METHODE_CHOICES = [
        ('moncash',  'MonCash'),
        ('natcash',  'NatCash'),
        ('virement', 'Virement bancaire'),
        ('cash',     'Espèces'),
        ('',         'Non spécifiée'),
    ]
    DEVISE_CHOICES = [
        ('usd', 'USD'),
        ('htg', 'HTG'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotisations')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES, default='usd')
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    methode_paiement = models.CharField(max_length=20, choices=METHODE_CHOICES, blank=True, default='')
    reference_paiement = models.CharField(max_length=100, blank=True)
    reference_plopplop = models.CharField(max_length=100, blank=True, help_text="Référence interne Plopplop")
    preuve_paiement = models.FileField(upload_to='cotisations/preuves/', blank=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date_debut} à {self.date_fin}"


class Opportunite(models.Model):
    """Offres d'emploi et appels d'offres"""
    TYPE_CHOICES = [
        ('emploi', 'Offre d\'emploi'),
        ('appel_offre', 'Appel d\'offres'),
        ('collaboration', 'Collaboration'),
    ]
    
    titre = models.CharField(max_length=200)
    type_opportunite = models.CharField(max_length=20, choices=TYPE_CHOICES)
    entreprise = models.CharField(max_length=200)
    description = models.TextField()
    competences_requises = models.TextField()
    localisation = models.CharField(max_length=200)
    salaire = models.CharField(max_length=100, blank=True)
    date_limite = models.DateField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    fichier_joint = models.FileField(upload_to='opportunites/', blank=True)
    publiee = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Opportunité"
        verbose_name_plural = "Opportunités"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.entreprise}"


class DocumentMembre(models.Model):
    """Documents réservés aux membres"""
    CATEGORIE_CHOICES = [
        ('certificat', 'Certificats'),
        ('formation', 'Formations'),
        ('reglementation', 'Réglementations'),
        ('template', 'Templates'),
        ('autre', 'Autre'),
    ]
    
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='documents_membres/')
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Document Membre"
        verbose_name_plural = "Documents Membres"
        ordering = ['-date_ajout']
    
    def __str__(self):
        return self.titre


class ForumCategorie(models.Model):
    """Catégories du forum membres"""
    nom = models.CharField(max_length=100)
    description = models.TextField()
    ordre = models.IntegerField(default=0)
    icone = models.CharField(max_length=50, default='forum')
    
    class Meta:
        verbose_name = "Catégorie de Forum"
        verbose_name_plural = "Catégories de Forum"
        ordering = ['ordre']
    
    def __str__(self):
        return self.nom


class ForumSujet(models.Model):
    """Sujets du forum"""
    categorie = models.ForeignKey(ForumCategorie, on_delete=models.CASCADE, related_name='sujets')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sujets_forum')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    epingle = models.BooleanField(default=False)
    verrouille = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    vues = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Sujet de Forum"
        verbose_name_plural = "Sujets de Forum"
        ordering = ['-epingle', '-date_modification']
    
    def __str__(self):
        return self.titre


class ForumReponse(models.Model):
    """Réponses aux sujets"""
    sujet = models.ForeignKey(ForumSujet, on_delete=models.CASCADE, related_name='reponses')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponses_forum')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Réponse de Forum"
        verbose_name_plural = "Réponses de Forum"
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Réponse de {self.auteur.get_full_name()} sur {self.sujet.titre}"