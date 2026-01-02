# src/apps/news/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField


class NewsCategory(models.Model):
    """Catégorie d'actualités"""
    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField("Slug", unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class NewsArticle(models.Model):
    """Article d'actualité"""
    NEWS_TYPE_CHOICES = [
        ('national', 'National'),
        ('international', 'International'),
    ]

    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='articles'
    )
    news_type = models.CharField(
        "Type d'actualité",
        max_length=20,
        choices=NEWS_TYPE_CHOICES,
        default='national'
    )
    
    # Contenu
    excerpt = models.TextField("Résumé", max_length=300, help_text="Court résumé de l'article")
    content = RichTextField("Contenu")
    
    # Image
    image = models.ImageField(
        "Image principale",
        upload_to='news/%Y/%m/',
        blank=True,
        null=True
    )
    image_caption = models.CharField("Légende de l'image", max_length=200, blank=True)
    
    # Métadonnées
    author = models.CharField("Auteur", max_length=100, blank=True)
    source = models.CharField("Source", max_length=200, blank=True)
    source_url = models.URLField("Lien source", blank=True)
    
    # Publication
    is_active = models.BooleanField("Publié", default=False)
    is_featured = models.BooleanField("À la une", default=False, help_text="Afficher sur la page d'accueil")
    published_at = models.DateTimeField("Date de publication", default=timezone.now)
    
    # Timestamps
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)
    
    # SEO
    meta_description = models.CharField(
        "Meta description",
        max_length=160,
        blank=True,
        help_text="Description pour les moteurs de recherche"
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_description:
            self.meta_description = self.excerpt[:160]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news:detail', kwargs={'slug': self.slug})