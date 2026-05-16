from django.db import models
from django.utils import timezone
from django.conf import settings
from io import BytesIO
from simple_history.models import HistoricalRecords
import qrcode


class TitreProfessionnel(models.Model):
    nom = models.CharField(max_length=100, help_text="Ex: Ingénieur Civil, Architecte, etc.")
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Titre Professionnel"
        verbose_name_plural = "Titres Professionnels"
        ordering = ['ordre']

    def __str__(self):
        return self.nom


class MembreActif(models.Model):
    numero = models.CharField(max_length=20, unique=True, help_text="Numéro d'identification unique")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    titre = models.ForeignKey(TitreProfessionnel, on_delete=models.PROTECT, related_name='membres')
    photo = models.ImageField(upload_to='membres/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    date_inscription = models.DateField(default=timezone.now)
    email_public = models.EmailField(
        blank=True,
        help_text="Email affiché publiquement sur la liste des membres (optionnel)"
    )
    telephone_public = models.CharField(
        max_length=30,
        blank=True,
        help_text="Téléphone affiché publiquement sur la liste des membres (optionnel)"
    )

    history = HistoricalRecords()

    class Meta:
        app_label = 'core'
        verbose_name = "Membre Actif"
        verbose_name_plural = "Membres Actifs"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.numero} - {self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class PageMembresActifs(models.Model):
    """Paramètres de la page Membres Actifs"""
    titre = models.CharField(max_length=200, default="Liste des Ingénieurs et Architectes Actifs")
    introduction = models.TextField(help_text="Texte d'introduction affiché en haut de la page")

    class Meta:
        app_label = 'core'
        verbose_name = "Configuration Page Membres Actifs"
        verbose_name_plural = "Configuration Page Membres Actifs"

    def __str__(self):
        return "Configuration Page Membres Actifs"


class ConfigurationCertificat(models.Model):
    """Singleton — paramètres visuels du certificat PDF (signature, nom du Président)."""
    nom_president = models.CharField(max_length=100, default="Président du CNIAH")
    titre_president = models.CharField(max_length=100, default="Président")
    signature_president = models.ImageField(
        upload_to='config/signatures/',
        blank=True,
        null=True,
        help_text="Image PNG transparente de la signature du Président"
    )
    logo_organisation = models.ImageField(
        upload_to='config/',
        blank=True,
        null=True,
        help_text="Logo alternatif pour le certificat (optionnel, utilise le logo principal sinon)"
    )
    texte_bas_page = models.TextField(
        blank=True,
        default="Ce certificat atteste de la qualité de membre actif en règle du Collège National des Ingénieurs et Architectes Haïtiens (CNIAH), créé par Décret-loi présidentiel du 25 mars 1974."
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Configuration Certificat"
        verbose_name_plural = "Configuration Certificat"

    def __str__(self):
        return "Configuration du Certificat CNIAH"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Certification(models.Model):
    STATUT_CHOICES = [
        ('valide', 'Valide'),
        ('expire', 'Expiré'),
        ('suspendu', 'Suspendu'),
    ]

    numero_certificat = models.CharField(max_length=50, unique=True)
    membre = models.ForeignKey(MembreActif, on_delete=models.CASCADE, related_name='certifications')
    date_delivrance = models.DateField()
    date_expiration = models.DateField(
        editable=False,
        help_text="Calculé automatiquement : premier 30 septembre après la date de délivrance × années de validité"
    )
    annees_validite = models.PositiveIntegerField(
        default=1,
        help_text="Nombre d'années de validité. L'expiration sera au 30 sept de l'année de délivrance + (N-1) ans."
    )
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='valide')

    history = HistoricalRecords()

    class Meta:
        app_label = 'core'
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['-date_delivrance']

    def __str__(self):
        return f"{self.numero_certificat} - {self.membre.nom_complet}"

    @staticmethod
    def calculer_expiration(date_delivrance, annees: int = 1):
        """Retourne le 30 septembre après N années de validité."""
        from datetime import date as date_type
        annee_base = date_delivrance.year
        if date_delivrance > date_type(annee_base, 9, 30):
            annee_base += 1
        annee_expiration = annee_base + (annees - 1)
        return date_type(annee_expiration, 9, 30)

    def save(self, *args, **kwargs):
        self.date_expiration = self.calculer_expiration(self.date_delivrance, self.annees_validite)
        super().save(*args, **kwargs)

    @property
    def est_valide(self):
        return self.statut == 'valide' and self.date_expiration >= timezone.now().date()

    def generate_qr_code(self):
        """Génère et stocke le QR code pointant vers la page de vérification."""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8002')
        qr_url = f"{site_url}/verifier-certification/?numero={self.numero_certificat}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        filename = f"qr_{self.numero_certificat}.png"
        self.qr_code.save(filename, buf, save=False)
