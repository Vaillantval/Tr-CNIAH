# src/apps/advertisements/models.py
from django.db import models
from django.utils import timezone


class Advertisement(models.Model):
    """Publicités sur le site"""
    POSITION_CHOICES = [
        ('banner', 'Bannière (haut de page)'),
        ('sidebar', 'Barre latérale'),
        ('footer', 'Pied de page'),
    ]

    title = models.CharField("Titre", max_length=200)
    image = models.ImageField("Image", upload_to='ads/')
    link = models.URLField("Lien", blank=True)
    position = models.CharField("Position", max_length=20, choices=POSITION_CHOICES)
    
    # Dates
    start_date = models.DateField("Date de début", default=timezone.now)
    end_date = models.DateField("Date de fin")
    
    # Options
    is_active = models.BooleanField("Actif", default=True)
    open_new_tab = models.BooleanField("Ouvrir dans un nouvel onglet", default=True)
    
    # Stats (optionnel)
    clicks = models.PositiveIntegerField("Clics", default=0, editable=False)
    
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.position})"

    def is_valid(self):
        """Vérifie si la pub est valide aujourd'hui"""
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date