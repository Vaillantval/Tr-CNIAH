from django.db import models
from django.utils.text import slugify


class Newsletter(models.Model):
    """Abonnements newsletter"""
    email = models.EmailField(unique=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Abonnement Newsletter"
        verbose_name_plural = "Abonnements Newsletter"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class DocumentCategory(models.Model):
    """Catégories pour les documents de référence"""
    CATEGORY_CHOICES = [
        ('architecture', 'Architecture'),
        ('regulation', 'Réglementation'),
        ('technical', 'Technique'),
        ('forms', 'Formulaires'),
        ('guides', 'Guides'),
    ]

    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField("Slug", unique=True, blank=True)
    category_type = models.CharField("Type", max_length=20, choices=CATEGORY_CHOICES, default='technical')
    description = models.TextField("Description", blank=True)
    icon = models.CharField("Icône", max_length=50, default='library_books',
                            help_text="Nom de l'icône Material Symbols")
    order = models.IntegerField("Ordre", default=0)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Catégorie de document"
        verbose_name_plural = "Catégories de documents"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ReferenceDocument(models.Model):
    """Documents de référence (PDF, DOCX, etc.)"""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('doc', 'Document Word'),
        ('xls', 'Excel'),
        ('ppt', 'PowerPoint'),
        ('zip', 'Archive ZIP'),
    ]

    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='documents'
    )
    description = models.TextField("Description")
    file = models.FileField("Fichier", upload_to='documents/%Y/%m/')
    file_type = models.CharField("Type de fichier", max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.CharField("Taille du fichier", max_length=20, blank=True,
                                 help_text="Ex: 4.2 MB")
    author = models.CharField("Auteur", max_length=100, blank=True)
    version = models.CharField("Version", max_length=20, blank=True)
    is_active = models.BooleanField("Publié", default=True)
    is_featured = models.BooleanField("Mis en avant", default=False)
    order = models.IntegerField("Ordre", default=0)
    download_count = models.PositiveIntegerField("Téléchargements", default=0, editable=False)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Document de référence"
        verbose_name_plural = "Documents de référence"
        ordering = ['-is_featured', 'order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.file_type and self.file:
            ext = self.file.name.split('.')[-1].lower()
            type_map = {
                'pdf': 'pdf',
                'doc': 'doc', 'docx': 'doc',
                'xls': 'xls', 'xlsx': 'xls',
                'ppt': 'ppt', 'pptx': 'ppt',
                'zip': 'zip', 'rar': 'zip'
            }
            self.file_type = type_map.get(ext, 'pdf')
        super().save(*args, **kwargs)

    def get_icon_color(self):
        colors = {
            'pdf': 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400',
            'doc': 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400',
            'xls': 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400',
            'ppt': 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400',
            'zip': 'text-gray-600 bg-gray-50 dark:bg-gray-900/20 dark:text-gray-400',
        }
        return colors.get(self.file_type, colors['pdf'])

    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])


class VideoResource(models.Model):
    """Ressources vidéo (YouTube, Vimeo, ou upload direct)"""
    VIDEO_TYPE_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('upload', 'Upload Direct'),
    ]

    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    series_name = models.CharField("Nom de la série", max_length=100, blank=True,
                                   help_text="Ex: ZAFE GOUDOUGOUDOU")
    episode_number = models.PositiveIntegerField("Numéro d'épisode", null=True, blank=True)
    description = models.TextField("Description")
    video_type = models.CharField("Type de vidéo", max_length=20, choices=VIDEO_TYPE_CHOICES)
    video_url = models.URLField("URL de la vidéo", blank=True,
                                help_text="Pour YouTube ou Vimeo")
    video_file = models.FileField("Fichier vidéo", upload_to='videos/%Y/%m/', blank=True,
                                  help_text="Pour upload direct")
    thumbnail = models.ImageField("Miniature", upload_to='video_thumbnails/%Y/%m/', blank=True, null=True)
    duration = models.CharField("Durée", max_length=20, blank=True, help_text="Ex: 15:30")
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='videos'
    )
    is_active = models.BooleanField("Publié", default=True)
    is_featured = models.BooleanField("Mis en avant", default=False)
    order = models.IntegerField("Ordre", default=0)
    view_count = models.PositiveIntegerField("Vues", default=0, editable=False)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Ressource vidéo"
        verbose_name_plural = "Ressources vidéo"
        ordering = ['series_name', 'episode_number', 'order', '-created_at']

    def __str__(self):
        if self.episode_number and self.series_name:
            return f"{self.series_name} - Épisode {self.episode_number}: {self.title}"
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def _extract_youtube_id(self):
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url or '')
            if match:
                return match.group(1)
        return None

    def get_embed_url(self):
        if self.video_type == 'youtube':
            video_id = self._extract_youtube_id()
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        elif self.video_type == 'vimeo':
            video_id = (self.video_url or '').split('/')[-1].split('?')[0]
            return f"https://player.vimeo.com/video/{video_id}"
        return None

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.video_type == 'youtube':
            video_id = self._extract_youtube_id()
            if video_id:
                return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return None

    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ImageGallery(models.Model):
    """Galerie d'images pour projets et références"""
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    image = models.ImageField("Image", upload_to='gallery/%Y/%m/')
    caption = models.CharField("Légende", max_length=300, blank=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='images'
    )
    is_active = models.BooleanField("Publié", default=True)
    order = models.IntegerField("Ordre", default=0)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Image de galerie"
        verbose_name_plural = "Galerie d'images"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
