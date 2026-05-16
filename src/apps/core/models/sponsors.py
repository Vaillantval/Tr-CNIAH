from django.db import models


class Sponsor(models.Model):
    """
    Partenaires institutionnels du CNIAH (sponsors officiels par niveau de partenariat).
    Différent des Publicités : un sponsor est une organisation partenaire qui soutient le CNIAH
    sur la durée, classée par niveau (Platine → Bronze). Son logo est affiché dans la section
    partenaires du site, pas dans des espaces publicitaires rotatifs.
    """
    NIVEAU_CHOICES = [
        ('platine', 'Platine'),
        ('or', 'Or'),
        ('argent', 'Argent'),
        ('bronze', 'Bronze'),
    ]

    nom = models.CharField(max_length=200)
    niveau = models.CharField(
        max_length=20,
        choices=NIVEAU_CHOICES,
        help_text="Niveau de partenariat (Platine = partenaire principal, Bronze = contributeur)"
    )
    logo = models.ImageField(
        upload_to='sponsors/',
        help_text="Logo du sponsor. Taille recommandée : 400 × 200 px, fond transparent (PNG)."
    )
    description = models.TextField(blank=True)
    url_site = models.URLField(blank=True, help_text="Site web du sponsor (optionnel)")
    ordre = models.IntegerField(default=0, help_text="Ordre d'affichage (les plus petits en premier)")
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Sponsor / Partenaire"
        verbose_name_plural = "Sponsors / Partenaires"
        ordering = ['ordre']

    def __str__(self):
        return f"{self.nom} ({self.get_niveau_display()})"
