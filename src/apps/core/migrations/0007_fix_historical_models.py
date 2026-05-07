# src/apps/core/migrations/0007_fix_historical_models.py
#
# Migration 0006 was hand-written with an incomplete set of fields for each
# HistoricalXxx model.  simple_history mirrors ALL model fields into the audit
# table, so the missing columns cause an IntegrityError whenever a record is
# saved after deployment.  This migration adds the absent fields.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_history_and_remove_sponsor'),
    ]

    operations = [

        # ── HistoricalMembreActif ────────────────────────────────────────────
        migrations.AddField(
            model_name='historicalmembreactif',
            name='photo',
            field=models.ImageField(blank=True, max_length=100, null=True, upload_to='membres/'),
        ),

        # ── HistoricalPlainte ────────────────────────────────────────────────
        migrations.AddField(
            model_name='historicalplainte',
            name='date_soumission',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalplainte',
            name='date_traitement',
            field=models.DateTimeField(blank=True, null=True),
        ),

        # ── HistoricalCertification ──────────────────────────────────────────
        migrations.AddField(
            model_name='historicalcertification',
            name='date_delivrance',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcertification',
            name='date_expiration',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalcertification',
            name='qr_code',
            field=models.ImageField(blank=True, max_length=100, null=True, upload_to='qr_codes/'),
        ),

        # ── HistoricalDemandeAdhesion ────────────────────────────────────────
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='statut_souhaite',
            field=models.CharField(default='postulant', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='titre',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='fonction',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='nif',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='telephone',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='adresse',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='diplome_1',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='diplome_2',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='cv_resume',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='don_montant',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='photo_identite',
            field=models.ImageField(blank=True, max_length=100, null=True, upload_to='adhesion/photos/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='copie_diplomes',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/diplomes/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='piece_identite',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/identites/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='cv_fichier',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/cvs/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='certificat_cniah',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/certificats/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='lettre_support',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/lettres/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='permis_sejour',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/permis/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='autres_documents',
            field=models.FileField(blank=True, max_length=100, null=True, upload_to='adhesion/autres/'),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='date_soumission',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaldemandeadhesion',
            name='notes_admin',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
