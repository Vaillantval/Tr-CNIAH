import factory
from django.utils import timezone
from apps.news.models import NewsCategory, NewsArticle


class NewsCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsCategory

    name = factory.Sequence(lambda n: f"Catégorie {n}")
    slug = factory.Sequence(lambda n: f"categorie-{n}")
    order = factory.Sequence(lambda n: n)


class NewsArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewsArticle

    title = factory.Sequence(lambda n: f"Article de test {n}")
    excerpt = "Extrait court de l'article."
    content = "<p>Contenu complet de l'article de test.</p>"
    news_type = 'national'
    category = factory.SubFactory(NewsCategoryFactory)
    status = 'published'
    published_at = factory.LazyFunction(timezone.now)


class DraftArticleFactory(NewsArticleFactory):
    status = 'draft'


class InternationalArticleFactory(NewsArticleFactory):
    news_type = 'international'
