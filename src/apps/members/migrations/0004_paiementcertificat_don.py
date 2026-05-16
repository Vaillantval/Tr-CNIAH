from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_cotisation_devise'),
        ('core', '0010_f4_f6_f8_contacts_plainte_certification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # F9 — PaiementCertificat
        migrations.CreateModel(
            name='PaiementCertificat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('devise', models.CharField(
                    choices=[('usd', 'USD'), ('htg', 'HTG')],
                    default='usd',
                    max_length=3,
                )),
                ('annees_payees', models.PositiveIntegerField(
                    default=1,
                    help_text="Nombre d'années couvertes par ce paiement",
                )),
                ('statut', models.CharField(
                    choices=[('en_attente', 'En attente'), ('valide', 'Validé'), ('refuse', 'Refusé')],
                    default='en_attente',
                    max_length=20,
                )),
                ('methode_paiement', models.CharField(
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
                )),
                ('reference_paiement', models.CharField(blank=True, max_length=100)),
                ('reference_plopplop', models.CharField(blank=True, max_length=100)),
                ('preuve_paiement', models.FileField(blank=True, upload_to='certificats/preuves/')),
                ('date_paiement', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='paiements_certificat',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('certification', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='paiements',
                    to='core.certification',
                )),
            ],
            options={
                'verbose_name': 'Paiement de Certification',
                'verbose_name_plural': 'Paiements de Certification',
                'ordering': ['-date_creation'],
            },
        ),

        # F9 — Don
        migrations.CreateModel(
            name='Don',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_donateur', models.CharField(
                    blank=True,
                    help_text='Pour les dons anonymes',
                    max_length=100,
                )),
                ('email_donateur', models.EmailField(blank=True, help_text='Pour les dons anonymes')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('devise', models.CharField(
                    choices=[('usd', 'USD'), ('htg', 'HTG')],
                    default='htg',
                    max_length=3,
                )),
                ('message', models.TextField(blank=True, help_text='Message accompagnant le don')),
                ('statut', models.CharField(
                    choices=[('recu', 'Reçu'), ('confirme', 'Confirmé')],
                    default='recu',
                    max_length=20,
                )),
                ('methode_paiement', models.CharField(
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
                )),
                ('reference_paiement', models.CharField(blank=True, max_length=100)),
                ('date_don', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='dons',
                    to=settings.AUTH_USER_MODEL,
                    help_text='Membre connecté (optionnel)',
                )),
            ],
            options={
                'verbose_name': 'Don',
                'verbose_name_plural': 'Dons',
                'ordering': ['-date_don'],
            },
        ),
    ]
