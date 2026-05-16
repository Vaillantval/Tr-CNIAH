# src/apps/advertisements/models.py
from django.db import models
from django.utils import timezone


class Advertisement(models.Model):
    """
    Espaces publicitaires payants affichés sur le site (bannière, barre latérale, pied de page).
    Différent des Sponsors : une publicité est achetée pour une période définie et s'affiche
    dans un emplacement précis du site. Elle peut être pour n'importe quelle organisation,
    pas forcément un partenaire du CNIAH.

    Tailles d'image recommandées :
      - Bannière (haut de page) : 1200 × 300 px
      - Barre latérale          :  300 × 250 px
      - Pied de page            :  728 ×  90 px
    Format : JPG ou PNG, moins de 500 Ko.
    """
    POSITION_CHOICES = [
        ('banner', 'Bannière (haut de page) — 1200 × 300 px'),
        ('sidebar', 'Barre latérale — 300 × 250 px'),
        ('footer', 'Pied de page — 728 × 90 px'),
    ]

    title = models.CharField("Titre", max_length=200)
    image = models.ImageField(
        "Image",
        upload_to='ads/',
        help_text=(
            "Bannière : 1200 × 300 px | Barre latérale : 300 × 250 px | "
            "Pied de page : 728 × 90 px. Format JPG/PNG, max 500 Ko."
        )
    )
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