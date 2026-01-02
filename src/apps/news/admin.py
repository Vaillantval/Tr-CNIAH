# src/apps/news/admin.py
from django.contrib import admin
from .models import NewsCategory, NewsArticle


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'news_type', 'is_featured', 'is_active', 'published_at']
    list_filter = ['is_active', 'is_featured', 'news_type', 'category', 'published_at']
    search_fields = ['title', 'excerpt', 'content', 'author']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'category', 'news_type')
        }),
        ('Contenu', {
            'fields': ('excerpt', 'content', 'image', 'image_caption')
        }),
        ('Métadonnées', {
            'fields': ('author', 'source', 'source_url')
        }),
        ('Publication', {
            'fields': ('is_active', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')