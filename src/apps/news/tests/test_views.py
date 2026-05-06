import pytest
from django.urls import reverse
from .factories import NewsArticleFactory, NewsCategoryFactory, DraftArticleFactory, InternationalArticleFactory


@pytest.mark.django_db
class TestNewsListView:
    def test_status_200(self, client):
        response = client.get(reverse('news:list'))
        assert response.status_code == 200

    def test_only_published_articles(self, client):
        NewsArticleFactory(status='published')
        DraftArticleFactory()
        response = client.get(reverse('news:list'))
        assert len(response.context['articles']) == 1

    def test_filter_by_type_national(self, client):
        NewsArticleFactory(news_type='national')
        InternationalArticleFactory()
        response = client.get(reverse('news:list') + '?type=national')
        articles = list(response.context['articles'])
        assert all(a.news_type == 'national' for a in articles)

    def test_filter_by_type_international(self, client):
        NewsArticleFactory(news_type='national')
        InternationalArticleFactory()
        response = client.get(reverse('news:list') + '?type=international')
        articles = list(response.context['articles'])
        assert all(a.news_type == 'international' for a in articles)

    def test_filter_by_category(self, client):
        cat = NewsCategoryFactory()
        other_cat = NewsCategoryFactory()
        a1 = NewsArticleFactory(category=cat)
        NewsArticleFactory(category=other_cat)
        response = client.get(reverse('news:list') + f'?category={cat.slug}')
        articles = list(response.context['articles'])
        assert len(articles) == 1
        assert articles[0].pk == a1.pk

    def test_pagination_9_per_page(self, client):
        for _ in range(12):
            NewsArticleFactory()
        response = client.get(reverse('news:list'))
        assert len(response.context['articles']) == 9

    def test_categories_in_context(self, client):
        NewsCategoryFactory()
        response = client.get(reverse('news:list'))
        assert 'categories' in response.context


@pytest.mark.django_db
class TestNewsDetailView:
    def test_status_200(self, client):
        article = NewsArticleFactory()
        response = client.get(reverse('news:detail', kwargs={'slug': article.slug}))
        assert response.status_code == 200

    def test_draft_returns_404(self, client):
        article = DraftArticleFactory()
        response = client.get(reverse('news:detail', kwargs={'slug': article.slug}))
        assert response.status_code == 404

    def test_related_articles_in_context(self, client):
        cat = NewsCategoryFactory()
        article = NewsArticleFactory(category=cat)
        NewsArticleFactory(category=cat)
        response = client.get(reverse('news:detail', kwargs={'slug': article.slug}))
        assert 'related_articles' in response.context
