from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_fix_photo_fields_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoresource',
            name='thumbnail',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='video_thumbnails/%Y/%m/',
                verbose_name='Miniature',
            ),
        ),
    ]
