from django.db import models


class ComiteDirection(models.Model):
    annee_debut = models.IntegerField()
    annee_fin = models.IntegerField()
    actif = models.BooleanField(default=False, help_text="Cocher si c'est le comité actuel")

    class Meta:
        app_label = 'core'
        verbose_name = "Comité de Direction"
        verbose_name_plural = "Comités de Direction"
        ordering = ['-annee_debut']

    def __str__(self):
        return f"Comité {self.annee_debut}-{self.annee_fin}"


class MembreComite(models.Model):
    POSTE_CHOICES = [
        ('president', 'Président'),
        ('vice_president', 'Vice-Président'),
        ('secretaire', 'Secrétaire Général'),
        ('tresorier', 'Trésorier'),
        ('conseiller', 'Conseiller'),
    ]

    comite = models.ForeignKey(ComiteDirection, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    poste = models.CharField(max_length=20, choices=POSTE_CHOICES)
    photo = models.ImageField(upload_to='comite/', blank=True, null=True)
    biographie = models.TextField()
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Membre du Comité"
        verbose_name_plural = "Membres du Comité"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.get_poste_display()}"


class CommissionApurement(models.Model):
    annee_debut = models.IntegerField()
    annee_fin = models.IntegerField()
    actif = models.BooleanField(default=False, help_text="Cocher si c'est la commission actuelle")
    description = models.TextField(blank=True, help_text="Texte explicatif des attributions")

    class Meta:
        app_label = 'core'
        verbose_name = "Commission d'Apurement"
        verbose_name_plural = "Commissions d'Apurement"
        ordering = ['-annee_debut']

    def __str__(self):
        return f"Commission d'Apurement {self.annee_debut}-{self.annee_fin}"


class MembreCommission(models.Model):
    commission = models.ForeignKey(CommissionApurement, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='commission/', blank=True, null=True)
    biographie = models.TextField()
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Membre de la Commission"
        verbose_name_plural = "Membres de la Commission"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class ConseilDiscipline(models.Model):
    annee_debut = models.IntegerField()
    annee_fin = models.IntegerField()
    actif = models.BooleanField(default=False, help_text="Cocher si c'est le conseil actuel")

    class Meta:
        app_label = 'core'
        verbose_name = "Conseil de Discipline"
        verbose_name_plural = "Conseils de Discipline"
        ordering = ['-annee_debut']

    def __str__(self):
        return f"Conseil de Discipline {self.annee_debut}-{self.annee_fin}"


class MembreConseil(models.Model):
    conseil = models.ForeignKey(ConseilDiscipline, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='conseil/', blank=True, null=True)
    biographie = models.TextField()
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Membre du Conseil"
        verbose_name_plural = "Membres du Conseil"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.prenom} {self.nom}"
