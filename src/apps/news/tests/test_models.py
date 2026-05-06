import pytest
from apps.news.models import NewsArticle
from .factories import NewsArticleFactory, NewsCategoryFactory


@pytest.mark.django_db
class TestNewsArticle:
    def test_slug_auto_generated(self):
        article = NewsArticleFactory(title="Mon premier article")
        assert article.slug == "mon-premier-article"

    def test_slug_collision_handled(self):
        NewsArticleFactory(title="Article duplicate")
        article2 = NewsArticleFactory(title="Article duplicate")
        assert article2.slug == "article-duplicate-1"

    def test_str(self):
        article = NewsArticleFactory(title="Titre test")
        assert str(article) == "Titre test"

    def test_draft_not_visible_by_default_in_queryset(self):
        from .factories import DraftArticleFactory
        DraftArticleFactory()
        assert NewsArticle.objects.filter(status='published').count() == 0

    def test_published_visible(self):
        NewsArticleFactory(status='published')
        assert NewsArticle.objects.filter(status='published').count() == 1


@pytest.mark.django_db
class TestNewsCategory:
    def test_slug_auto_generated(self):
        cat = NewsCategoryFactory(name="Génie Civil")
        assert cat.slug == "genie-civil"

    def test_str(self):
        cat = NewsCategoryFactory(name="Catégorie X")
        assert str(cat) == "Catégorie X"
