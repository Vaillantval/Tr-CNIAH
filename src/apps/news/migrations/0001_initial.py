# src/apps/news/migrations/0001_initial.py

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='Slug')),
                ('order', models.IntegerField(default=0, verbose_name='Ordre')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'verbose_name_plural': 'Catégories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, verbose_name='Titre')),
                ('slug', models.SlugField(blank=True, max_length=320, unique=True, verbose_name='Slug')),
                ('excerpt', models.TextField(blank=True, help_text='Résumé court affiché en aperçu', verbose_name='Extrait')),
                ('content', models.TextField(help_text="Contenu complet de l'article (HTML accepté)", verbose_name='Contenu')),
                ('news_type', models.CharField(
                    choices=[('national', 'National'), ('international', 'International')],
                    default='national',
                    max_length=20,
                    verbose_name="Type d'actualité"
                )),
                ('image', models.ImageField(blank=True, null=True, upload_to='news/%Y/%m/', verbose_name='Image principale')),
                ('image_caption', models.CharField(blank=True, max_length=300, verbose_name="Légende de l'image")),
                ('author', models.CharField(blank=True, max_length=150, verbose_name='Auteur')),
                ('source', models.CharField(blank=True, max_length=200, verbose_name='Source')),
                ('source_url', models.URLField(blank=True, verbose_name='URL de la source')),
                ('status', models.CharField(
                    choices=[('draft', 'Brouillon'), ('published', 'Publié')],
                    default='draft',
                    max_length=20,
                    verbose_name='Statut'
                )),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de publication')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('category', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='articles',
                    to='news.newscategory',
                    verbose_name='Catégorie'
                )),
            ],
            options={
                'verbose_name': "Article d'actualité",
                'verbose_name_plural': "Articles d'actualité",
                'ordering': ['-published_at'],
            },
        ),
    ]