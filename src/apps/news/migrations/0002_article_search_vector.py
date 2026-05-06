import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AddIndex(
            model_name='newsarticle',
            index=django.contrib.postgres.indexes.GinIndex(
                fields=['search_vector'],
                name='news_article_search_idx',
            ),
        ),
    ]
