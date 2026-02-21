# src/apps/news/models.py

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class NewsCategory(models.Model):
    """Catégorie d'article de news."""
    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField("Slug", unique=True, blank=True)
    order = models.IntegerField("Ordre", default=0)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class NewsArticle(models.Model):
    """Article de news (national ou international)."""

    NEWS_TYPE_CHOICES = [
        ('national', 'National'),
        ('international', 'International'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]

    # Champs principaux
    title = models.CharField("Titre", max_length=300)
    slug = models.SlugField("Slug", unique=True, blank=True, max_length=320)
    excerpt = models.TextField("Extrait", blank=True, help_text="Résumé court affiché en aperçu")
    content = models.TextField("Contenu", help_text="Contenu complet de l'article (HTML accepté)")

    # Classification
    news_type = models.CharField(
        "Type d'actualité",
        max_length=20,
        choices=NEWS_TYPE_CHOICES,
        default='national'
    )
    category = models.ForeignKey(
        NewsCategory,
        verbose_name="Catégorie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )

    # Média
    image = models.ImageField(
        "Image principale",
        upload_to='news/%Y/%m/',
        blank=True,
        null=True
    )
    image_caption = models.CharField("Légende de l'image", max_length=300, blank=True)

    # Métadonnées
    author = models.CharField("Auteur", max_length=150, blank=True)
    source = models.CharField("Source", max_length=200, blank=True)
    source_url = models.URLField("URL de la source", blank=True)

    # Publication
    status = models.CharField("Statut", max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField("Date de publication", default=timezone.now)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Article d'actualité"
        verbose_name_plural = "Articles d'actualité"
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while NewsArticle.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)