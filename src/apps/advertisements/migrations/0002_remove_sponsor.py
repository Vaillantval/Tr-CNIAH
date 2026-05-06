from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Sponsor',
        ),
    ]
