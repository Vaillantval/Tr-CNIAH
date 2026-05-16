from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_videoresource_thumbnail_optional'),
    ]

    operations = [
        # F4 — Champs contact publics sur MembreActif
        migrations.AddField(
            model_name='membreactif',
            name='email_public',
            field=models.EmailField(
                blank=True,
                help_text="Email affiché publiquement sur la liste des membres (optionnel)",
            ),
        ),
        migrations.AddField(
            model_name='membreactif',
            name='telephone_public',
            field=models.CharField(
                blank=True,
                help_text="Téléphone affiché publiquement sur la liste des membres (optionnel)",
                max_length=30,
            ),
        ),

        # F8 — ConfigurationCertificat (singleton)
        migrations.CreateModel(
            name='ConfigurationCertificat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_president', models.CharField(default='Président du CNIAH', max_length=100)),
                ('titre_president', models.CharField(default='Président', max_length=100)),
                ('signature_president', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='config/signatures/',
                    help_text='Image PNG transparente de la signature du Président',
                )),
                ('logo_organisation', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='config/',
                    help_text='Logo alternatif pour le certificat (optionnel)',
                )),
                ('texte_bas_page', models.TextField(
                    blank=True,
                    default=(
                        'Ce certificat atteste de la qualité de membre actif en règle du Collège National '
                        'des Ingénieurs et Architectes Haïtiens (CNIAH), créé par Décret-loi présidentiel '
                        'du 25 mars 1974.'
                    ),
                )),
            ],
            options={
                'verbose_name': 'Configuration Certificat',
                'verbose_name_plural': 'Configuration Certificat',
            },
        ),

        # F8 — Ajout annees_validite sur Certification
        migrations.AddField(
            model_name='certification',
            name='annees_validite',
            field=models.PositiveIntegerField(
                default=1,
                help_text="Nombre d'années de validité.",
            ),
        ),

        # F8 — date_expiration devient non-editable
        migrations.AlterField(
            model_name='certification',
            name='date_expiration',
            field=models.DateField(
                editable=False,
                help_text="Calculé automatiquement : premier 30 septembre après la date de délivrance × années de validité",
            ),
        ),

        # F6 — membre_accuse FK sur Plainte
        migrations.AddField(
            model_name='plainte',
            name='membre_accuse',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='plaintes_contre',
                to='core.membreactif',
                verbose_name='Membre accusé',
                help_text="Sélectionner le membre actif visé par la plainte",
            ),
        ),

        # F6 — membre_concerne devient optionnel (rétro-compat)
        migrations.AlterField(
            model_name='plainte',
            name='membre_concerne',
            field=models.CharField(
                blank=True,
                help_text="Nom libre (héritage — utiliser 'membre_accuse' pour les nouvelles plaintes)",
                max_length=200,
            ),
        ),

        # Historique — HistoricalMembreActif sync
        migrations.AddField(
            model_name='historicalmembreactif',
            name='email_public',
            field=models.EmailField(blank=True),
        ),
        migrations.AddField(
            model_name='historicalmembreactif',
            name='telephone_public',
            field=models.CharField(blank=True, max_length=30),
        ),

        # Historique — HistoricalPlainte sync
        migrations.AddField(
            model_name='historicalplainte',
            name='membre_accuse',
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='+',
                to='core.membreactif',
                verbose_name='Membre accusé',
            ),
        ),
        migrations.AlterField(
            model_name='historicalplainte',
            name='membre_concerne',
            field=models.CharField(blank=True, max_length=200),
        ),

        # Historique — HistoricalCertification sync
        migrations.AddField(
            model_name='historicalcertification',
            name='annees_validite',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='historicalcertification',
            name='date_expiration',
            field=models.DateField(editable=False),
        ),
    ]
