# src\apps\core\migrations\0005_biographie_richtext_demande_adhesion.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_categoryformation_categorynorme_comitedirection_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandeAdhesion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_demande', models.CharField(
                    choices=[('admission', 'Nouvelle admission'), ('mise_a_jour', 'Mise à jour de statut')],
                    default='admission', max_length=20, verbose_name='Type de demande',
                )),
                ('statut_demande', models.CharField(
                    choices=[
                        ('en_attente', 'En attente'),
                        ('en_cours', "En cours d'examen"),
                        ('approuvee', 'Approuvée'),
                        ('rejetee', 'Rejetée'),
                    ],
                    default='en_attente', max_length=20, verbose_name='Statut de la demande',
                )),
                ('statut_souhaite', models.CharField(
                    choices=[('membre', 'Membre'), ('postulant', 'Postulant')],
                    default='postulant', max_length=20, verbose_name='Statut souhaité',
                )),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('titre', models.CharField(max_length=100, verbose_name='Titre professionnel')),
                ('fonction', models.CharField(blank=True, max_length=200, verbose_name='Fonction')),
                ('nif', models.CharField(blank=True, max_length=50, verbose_name='NIF')),
                ('telephone', models.CharField(max_length=30, verbose_name='Téléphone')),
                ('email', models.EmailField(verbose_name='Adresse courriel')),
                ('adresse', models.TextField(verbose_name='Adresse')),
                ('diplome_1', models.CharField(max_length=200, verbose_name='Diplôme 1 (avec année)')),
                ('diplome_2', models.CharField(blank=True, max_length=200, verbose_name='Diplôme 2 (avec année)')),
                ('cv_resume', models.TextField(blank=True, verbose_name='Curriculum Vitae (résumé)')),
                ('don_montant', models.DecimalField(
                    blank=True, decimal_places=2, max_digits=10, null=True,
                    verbose_name='Don (montant en HTG)',
                )),
                ('photo_identite', models.ImageField(
                    blank=True, null=True, upload_to='adhesion/photos/',
                    verbose_name='Photo d\'identité 2"×2"',
                )),
                ('copie_diplomes', models.FileField(
                    blank=True, null=True, upload_to='adhesion/diplomes/',
                    verbose_name='Copie du/des diplôme(s)',
                )),
                ('piece_identite', models.FileField(
                    blank=True, null=True, upload_to='adhesion/identites/',
                    verbose_name="Pièce d'identité",
                )),
                ('cv_fichier', models.FileField(
                    blank=True, null=True, upload_to='adhesion/cvs/',
                    verbose_name='CV (fichier)',
                )),
                ('certificat_cniah', models.FileField(
                    blank=True, null=True, upload_to='adhesion/certificats/',
                    verbose_name='Certificat CNIAH',
                )),
                ('lettre_support', models.FileField(
                    blank=True, null=True, upload_to='adhesion/lettres/',
                    verbose_name='Lettre de support',
                )),
                ('permis_sejour', models.FileField(
                    blank=True, null=True, upload_to='adhesion/permis/',
                    verbose_name='Permis de séjour',
                )),
                ('autres_documents', models.FileField(
                    blank=True, null=True, upload_to='adhesion/autres/',
                    verbose_name='Autres documents',
                )),
                ('date_soumission', models.DateTimeField(auto_now_add=True, verbose_name='Date de soumission')),
                ('notes_admin', models.TextField(blank=True, verbose_name='Notes administratives')),
            ],
            options={
                'verbose_name': "Demande d'Adhésion",
                'verbose_name_plural': "Demandes d'Adhésion",
                'ordering': ['-date_soumission'],
            },
        ),
    ]