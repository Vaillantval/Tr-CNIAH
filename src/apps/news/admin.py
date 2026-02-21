# src/apps/news/admin.py

from django.contrib import admin
from .models import NewsCategory, NewsArticle


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'news_type', 'category', 'status', 'published_at', 'author']
    list_filter = ['status', 'news_type', 'category', 'published_at']
    search_fields = ['title', 'excerpt', 'content', 'author']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'news_type']
    date_hierarchy = 'published_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Classification', {
            'fields': ('news_type', 'category', 'status', 'published_at')
        }),
        ('Média', {
            'fields': ('image', 'image_caption')
        }),
        ('Métadonnées', {
            'fields': ('author', 'source', 'source_url')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )