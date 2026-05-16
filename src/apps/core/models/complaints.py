import random
import string

from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from .members import MembreActif


class Plainte(models.Model):
    TYPE_PLAINTE_CHOICES = [
        ('ethique', "Violation d'éthique professionnelle"),
        ('competence', 'Compétence professionnelle'),
        ('qualite', 'Qualité des travaux'),
        ('contractuel', 'Litige contractuel'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('soumise', 'Soumise'),
        ('en_cours', "En cours d'examen"),
        ('traitee', 'Traitée'),
        ('classee', 'Classée'),
    ]

    numero_reference = models.CharField(max_length=50, unique=True, editable=False)
    nom_plaignant = models.CharField(max_length=100)
    email_plaignant = models.EmailField()
    telephone = models.CharField(max_length=20)
    membre_accuse = models.ForeignKey(
        MembreActif,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plaintes_contre',
        verbose_name="Membre accusé",
        help_text="Sélectionner le membre actif visé par la plainte"
    )
    membre_concerne = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nom libre (héritage — utiliser 'membre_accuse' pour les nouvelles plaintes)"
    )
    type_plainte = models.CharField(max_length=20, choices=TYPE_PLAINTE_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='soumise')
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    notes_internes = models.TextField(blank=True, help_text="Notes pour usage interne uniquement")

    history = HistoricalRecords()

    class Meta:
        app_label = 'core'
        verbose_name = "Plainte"
        verbose_name_plural = "Plaintes"
        ordering = ['-date_soumission']

    def __str__(self):
        return f"{self.numero_reference} - {self.nom_plaignant}"

    def save(self, *args, **kwargs):
        if not self.numero_reference:
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=4))
            self.numero_reference = f"PL-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class DocumentPlainte(models.Model):
    plainte = models.ForeignKey(Plainte, on_delete=models.CASCADE, related_name='documents')
    fichier = models.FileField(upload_to='plaintes/')
    nom_fichier = models.CharField(max_length=200)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Document de Plainte"
        verbose_name_plural = "Documents de Plainte"

    def __str__(self):
        return self.nom_fichier
