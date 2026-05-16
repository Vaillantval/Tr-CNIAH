from django.db import models
from simple_history.models import HistoricalRecords


class DemandeAdhesion(models.Model):
    """Formulaire de demande d'admission au CNIAH (membre-01)"""

    TYPE_CHOICES = [
        ('admission', 'Nouvelle admission'),
        ('mise_a_jour', 'Mise à jour de statut'),
    ]
    STATUT_DEMANDE_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', "En cours d'examen"),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
    ]
    STATUT_MEMBRE_CHOICES = [
        ('membre', 'Membre'),
        ('postulant', 'Postulant'),
    ]

    type_demande = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='admission',
        verbose_name="Type de demande",
    )
    statut_demande = models.CharField(
        max_length=20, choices=STATUT_DEMANDE_CHOICES, default='en_attente',
        verbose_name="Statut de la demande",
    )
    statut_souhaite = models.CharField(
        max_length=20, choices=STATUT_MEMBRE_CHOICES, default='postulant',
        verbose_name="Statut souhaité",
    )

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    titre = models.CharField(max_length=100, verbose_name="Titre professionnel")
    fonction = models.CharField(max_length=200, blank=True, verbose_name="Fonction")
    nif = models.CharField(max_length=50, blank=True, verbose_name="NIF")
    telephone = models.CharField(max_length=30, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Adresse courriel")
    adresse = models.TextField(verbose_name="Adresse")

    diplome_1 = models.CharField(max_length=200, verbose_name="Diplôme 1 (avec année)")
    diplome_2 = models.CharField(max_length=200, blank=True, verbose_name="Diplôme 2 (avec année)")
    cv_resume = models.TextField(blank=True, verbose_name="Curriculum Vitae (résumé)")

    don_montant = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Don (montant en HTG)",
    )

    photo_identite = models.ImageField(
        upload_to='adhesion/photos/', blank=True, null=True,
        verbose_name='Photo d\'identité 2"×2"',
    )
    copie_diplomes = models.FileField(
        upload_to='adhesion/diplomes/', blank=True, null=True,
        verbose_name="Copie du/des diplôme(s)",
    )
    piece_identite = models.FileField(
        upload_to='adhesion/identites/', blank=True, null=True,
        verbose_name="Pièce d'identité",
    )
    cv_fichier = models.FileField(
        upload_to='adhesion/cvs/', blank=True, null=True,
        verbose_name="CV (fichier)",
    )
    certificat_cniah = models.FileField(
        upload_to='adhesion/certificats/', blank=True, null=True,
        verbose_name="Certificat CNIAH",
    )
    lettre_support = models.FileField(
        upload_to='adhesion/lettres/', blank=True, null=True,
        verbose_name="Lettre de support",
    )
    permis_sejour = models.FileField(
        upload_to='adhesion/permis/', blank=True, null=True,
        verbose_name="Permis de séjour",
    )
    autres_documents = models.FileField(
        upload_to='adhesion/autres/', blank=True, null=True,
        verbose_name="Autres documents",
    )

    date_soumission = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    notes_admin = models.TextField(blank=True, verbose_name="Notes administratives")

    history = HistoricalRecords()

    class Meta:
        app_label = 'core'
        verbose_name = "Demande d'Adhésion"
        verbose_name_plural = "Demandes d'Adhésion"
        ordering = ['-date_soumission']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_statut_demande_display()})"
