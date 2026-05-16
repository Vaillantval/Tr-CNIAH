from django.db import migrations


def clear_membre_actif(apps, schema_editor):
    User = apps.get_model('members', 'User')
    MembreActif = apps.get_model('core', 'MembreActif')

    # Unlink all users first so the FK allows deletion
    User.objects.update(membre_actif=None)

    # Delete every MembreActif row so the admin starts from a clean slate
    MembreActif.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_add_membre_fields_to_user'),
        ('core', '0011_remove_unused_models'),
    ]

    operations = [
        migrations.RunPython(clear_membre_actif, migrations.RunPython.noop),
    ]
