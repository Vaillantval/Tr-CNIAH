from django.db import migrations, models
import django.db.models.deletion


def create_groupe_membres_actifs(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Membres Actifs')


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_paiementcertificat_don'),
        ('core', '0011_remove_unused_models'),
    ]

    operations = [
        # Changer membre_actif de CASCADE → SET_NULL
        migrations.AlterField(
            model_name='user',
            name='membre_actif',
            field=models.OneToOneField(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='user_account',
                to='core.membreactif',
            ),
        ),

        # Numéro de membre
        migrations.AddField(
            model_name='user',
            name='numero_membre',
            field=models.CharField(
                blank=True, max_length=20, null=True, unique=True,
                verbose_name='Numéro de membre',
            ),
        ),

        # Titre professionnel
        migrations.AddField(
            model_name='user',
            name='titre',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='users',
                to='core.titreprofessionnel',
                verbose_name='Titre professionnel',
            ),
        ),

        # Photo
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='membres/',
                verbose_name='Photo',
            ),
        ),

        # Date d'inscription
        migrations.AddField(
            model_name='user',
            name='date_inscription',
            field=models.DateField(
                blank=True, null=True,
                verbose_name="Date d'inscription",
            ),
        ),

        # Email public
        migrations.AddField(
            model_name='user',
            name='email_public',
            field=models.EmailField(blank=True, verbose_name='Email public'),
        ),

        # Téléphone public
        migrations.AddField(
            model_name='user',
            name='telephone_public',
            field=models.CharField(
                blank=True, max_length=30,
                verbose_name='Téléphone public',
            ),
        ),

        # Créer le groupe "Membres Actifs"
        migrations.RunPython(create_groupe_membres_actifs, migrations.RunPython.noop),
    ]
