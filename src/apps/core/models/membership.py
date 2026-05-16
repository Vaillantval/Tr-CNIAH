from django.db import models
from django.core.validators import FileExtensionValidator


class MembershipDocument(models.Model):
    """Documents pour l'adhésion au CNIAH"""
    MEMBER_TYPE_CHOICES = [
        ('national', 'Professionnels Nationaux'),
        ('international', 'Professionnels Internationaux'),
        ('both', 'Les deux'),
    ]

    title = models.CharField("Titre", max_length=200)
    description = models.TextField("Description", blank=True)
    file = models.FileField("Fichier", upload_to='membership/%Y/%m/')
    file_size = models.CharField("Taille du fichier", max_length=20, blank=True,
                                 help_text="Ex: 2.3 MB")
    icon = models.CharField("Icône", max_length=50, default='description',
                            help_text="Nom de l'icône Material Symbols")
    member_type = models.CharField(
        "Type de membre",
        max_length=20,
        choices=MEMBER_TYPE_CHOICES,
        default='both'
    )
    is_active = models.BooleanField("Actif", default=True)
    order = models.IntegerField("Ordre d'affichage", default=0)
    download_count = models.PositiveIntegerField("Téléchargements", default=0, editable=False)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Document d'adhésion"
        verbose_name_plural = "Documents d'adhésion"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return 'FILE'

    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])


class CotisationDocument(models.Model):
    titre = models.CharField(max_length=200)
    fichier = models.FileField(upload_to='cotisation/')
    date_ajout = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Document de Cotisation"
        verbose_name_plural = "Documents de Cotisation"
        ordering = ['-date_ajout']

    def __str__(self):
        return self.titre


class DocumentHistorique(models.Model):
    nom = models.CharField(max_length=200, help_text="Ex: Décret-loi 25 Mars 1974")
    fichier = models.FileField(upload_to='historique/', validators=[FileExtensionValidator(['pdf'])])
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Document Historique"
        verbose_name_plural = "Documents Historiques"
        ordering = ['ordre']

    def __str__(self):
        return self.nom
