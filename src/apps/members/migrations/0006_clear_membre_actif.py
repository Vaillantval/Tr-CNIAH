from django.db import migrations


class Migration(migrations.Migration):
    """
    Originally intended to clear MembreActif records.
    Kept as a no-op so the migration history stays consistent.
    MembreActif records are now managed via the User post_save signal.
    """

    dependencies = [
        ('members', '0005_add_membre_fields_to_user'),
        ('core', '0011_remove_unused_models'),
    ]

    operations = []
