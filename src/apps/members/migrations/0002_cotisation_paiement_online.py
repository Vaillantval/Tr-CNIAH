from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotisation',
            name='methode_paiement',
            field=models.CharField(
                blank=True,
                choices=[
                    ('moncash', 'MonCash'),
                    ('natcash', 'NatCash'),
                    ('virement', 'Virement bancaire'),
                    ('cash', 'Espèces'),
                    ('', 'Non spécifiée'),
                ],
                default='',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='cotisation',
            name='reference_plopplop',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Référence interne Plopplop',
                max_length=100,
            ),
            preserve_default=False,
        ),
    ]
