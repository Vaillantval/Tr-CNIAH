from django.db import models
from django.core.validators import FileExtensionValidator


class CategoryNorme(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0)
    icone = models.CharField(max_length=50, default='description',
                             help_text="Nom de l'icône Material Symbols")

    class Meta:
        app_label = 'core'
        verbose_name = "Catégorie de Norme"
        verbose_name_plural = "Catégories de Normes"
        ordering = ['ordre']

    def __str__(self):
        return self.nom


class Norme(models.Model):
    titre = models.CharField(max_length=200)
    version = models.CharField(max_length=50)
    date_publication = models.DateField()
    categorie = models.ForeignKey(CategoryNorme, on_delete=models.PROTECT, related_name='normes')
    fichier = models.FileField(upload_to='normes/', validators=[FileExtensionValidator(['pdf'])])
    description = models.TextField()
    actif = models.BooleanField(default=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Norme"
        verbose_name_plural = "Normes"
        ordering = ['-date_publication']

    def __str__(self):
        return f"{self.titre} - {self.version}"
