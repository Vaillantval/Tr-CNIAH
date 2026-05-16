# src/apps/news/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from .models import NewsArticle, NewsCategory


class NewsListView(ListView):
    """Liste des articles de news avec filtrage par type, catégorie et recherche full-text."""
    model = NewsArticle
    template_name = 'pages/news/list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        queryset = NewsArticle.objects.filter(
            status='published'
        ).select_related('category').order_by('-published_at')

        news_type = self.request.GET.get('type')
        if news_type in ('national', 'international'):
            queryset = queryset.filter(news_type=news_type)

        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        q = self.request.GET.get('q', '').strip()
        if q:
            # Recherche full-text via search_vector si disponible, sinon fallback icontains
            if queryset.filter(search_vector__isnull=False).exists():
                search_query = SearchQuery(q, config='french')
                queryset = queryset.filter(
                    search_vector=search_query
                ).annotate(rank=SearchRank(F('search_vector'), search_query)).order_by('-rank')
            else:
                queryset = queryset.filter(
                    title__icontains=q
                ) | queryset.filter(excerpt__icontains=q)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = NewsCategory.objects.all()
        context['current_type'] = self.request.GET.get('type', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
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

        related = NewsArticle.objects.filter(status='published').exclude(pk=article.pk)
        if article.category:
            related = related.filter(category=article.category)
        else:
            related = related.filter(news_type=article.news_type)

        context['related_articles'] = related.order_by('-published_at')[:3]
        return context
