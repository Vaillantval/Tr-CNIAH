# src/apps/news/views.py
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import NewsArticle, NewsCategory

class NewsListView(ListView):
    model = NewsArticle
    template_name = 'news/list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = NewsArticle.objects.filter(
            is_active=True,
            published_at__lte=timezone.now()
        )
        
        # Filtrer par type si spécifié
        news_type = self.request.GET.get('type')
        if news_type in ['national', 'international']:
            queryset = queryset.filter(news_type=news_type)
        
        # Filtrer par catégorie si spécifiée
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
    model = NewsArticle
    template_name = 'news/detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    
    def get_queryset(self):
        return NewsArticle.objects.filter(
            is_active=True,
            published_at__lte=timezone.now()
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Articles similaires (même catégorie ou type)
        context['related_articles'] = NewsArticle.objects.filter(
            is_active=True,
            published_at__lte=timezone.now()
        ).exclude(
            id=self.object.id
        ).filter(
            category=self.object.category
        )[:3]
        
        return context