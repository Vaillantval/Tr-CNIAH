from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_cotisation_paiement_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotisation',
            name='devise',
            field=models.CharField(
                choices=[('usd', 'USD'), ('htg', 'HTG')],
                default='usd',
                max_length=3,
            ),
        ),
    ]
