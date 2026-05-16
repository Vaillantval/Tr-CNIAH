from django.db import models


class CategoryFormation(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        verbose_name = "Catégorie de Formation"
        verbose_name_plural = "Catégories de Formation"
        ordering = ['ordre']

    def __str__(self):
        return self.nom


class FormationContent(models.Model):
    TYPE_CONTENU_CHOICES = [
        ('video', 'Vidéo'),
        ('image', 'Image'),
        ('pdf', 'Document PDF'),
        ('groupe_images', "Groupe d'images"),
    ]

    titre = models.CharField(max_length=200)
    date_formation = models.DateField()
    type_contenu = models.CharField(max_length=20, choices=TYPE_CONTENU_CHOICES)
    categorie = models.ForeignKey(CategoryFormation, on_delete=models.CASCADE, related_name='formations')
    video_url = models.URLField(blank=True, null=True, help_text="URL YouTube ou Vimeo")
    fichier = models.FileField(upload_to='formations/', blank=True, null=True)
    description = models.TextField()
    ordre = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Contenu de Formation"
        verbose_name_plural = "Contenus de Formation"
        ordering = ['-date_formation', 'ordre']

    def __str__(self):
        return f"{self.titre} ({self.date_formation})"

    def get_embed_url(self):
        import re
        url = self.video_url or ''
        if 'youtube.com' in url or 'youtu.be' in url:
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
                r'youtube\.com\/embed\/([^&\n?#]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return f"https://www.youtube.com/embed/{match.group(1)}?rel=0&modestbranding=1"
        elif 'vimeo.com' in url:
            video_id = url.split('/')[-1].split('?')[0]
            return f"https://player.vimeo.com/video/{video_id}"
        return None


class FormationImage(models.Model):
    formation = models.ForeignKey(FormationContent, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='formations/images/')
    legende = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        ordering = ['ordre']

    def __str__(self):
        return f"Image pour {self.formation.titre}"


class HonneurMerite(models.Model):
    TYPE_CONTENU_CHOICES = [
        ('video', 'Vidéo'),
        ('images', 'Images'),
        ('texte', 'Texte seulement'),
    ]

    annee = models.IntegerField()
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_contenu = models.CharField(max_length=20, choices=TYPE_CONTENU_CHOICES)
    video_url = models.URLField(blank=True, null=True)
    ordre = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Honneur et Mérite"
        verbose_name_plural = "Honneurs et Mérites"
        ordering = ['-annee', 'ordre']

    def __str__(self):
        return f"{self.annee} - {self.titre}"

    def get_embed_url(self):
        import re
        url = self.video_url or ''
        if 'youtube.com' in url or 'youtu.be' in url:
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
                r'youtube\.com\/embed\/([^&\n?#]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return f"https://www.youtube.com/embed/{match.group(1)}?rel=0&modestbranding=1"
        elif 'vimeo.com' in url:
            video_id = url.split('/')[-1].split('?')[0]
            return f"https://player.vimeo.com/video/{video_id}"
        return None


class HonneurMeriteImage(models.Model):
    honneur = models.ForeignKey(HonneurMerite, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='honneur_merite/')
    legende = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        ordering = ['ordre']

    def __str__(self):
        return f"Image pour {self.honneur.titre}"
