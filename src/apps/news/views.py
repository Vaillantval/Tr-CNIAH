# src/apps/news/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import NewsArticle, NewsCategory


class NewsListView(ListView):
    """Liste des articles de news avec filtrage par type et catégorie."""
    model = NewsArticle
    template_name = 'pages/news/list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        queryset = NewsArticle.objects.filter(
            status='published'
        ).select_related('category').order_by('-published_at')

        # Filtre par type (national/international)
        news_type = self.request.GET.get('type')
        if news_type in ('national', 'international'):
            queryset = queryset.filter(news_type=news_type)

        # Filtre par catégorie (slug)
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = NewsCategory.objects.all()
        context['current_type'] = self.request.GET.get('type', '')
        context['current_category'] = self.request.GET.get('category', '')
        return context


class NewsDetailView(DetailView):
    """Détail d'un article de news."""
    model = NewsArticle
    template_name = 'pages/news/detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return NewsArticle.objects.filter(status='published').select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Articles similaires (même type ou même catégorie, excluant l'article courant)
        related = NewsArticle.objects.filter(
            status='published'
        ).exclude(pk=article.pk)

        if article.category:
            related = related.filter(category=article.category)
        else:
            related = related.filter(news_type=article.news_type)

        context['related_articles'] = related.order_by('-published_at')[:3]
        return context