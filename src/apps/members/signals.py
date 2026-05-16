# src/apps/members/signals.py
# Guard against re-entrant saves triggered by this signal itself
_syncing_users = set()


def sync_membre_actif(sender, instance, **kwargs):
    """
    Maintain MembreActif in sync with User.
    When a User with a numero_membre is saved, the corresponding MembreActif
    is created (or updated) automatically so that existing FK relationships
    (Certification, Plainte, etc.) continue to work.
    """
    if instance.pk in _syncing_users or not instance.numero_membre:
        return

    _syncing_users.add(instance.pk)
    try:
        from apps.core.models import MembreActif, TitreProfessionnel

        membre = None

        # Try the already-linked MembreActif first
        if instance.membre_actif_id:
            try:
                membre = MembreActif.objects.get(pk=instance.membre_actif_id)
            except MembreActif.DoesNotExist:
                membre = None

        # Fall back: look up by numero
        if membre is None:
            membre = MembreActif.objects.filter(numero=instance.numero_membre).first()

        if membre is None:
            # Titre is required on MembreActif — use a default if not set
            titre = instance.titre
            if titre is None:
                titre = TitreProfessionnel.objects.order_by('ordre').first()
            if titre is None:
                # Cannot create MembreActif without a titre; skip silently
                return
            membre = MembreActif(numero=instance.numero_membre, titre=titre)

        # Sync all member fields from User → MembreActif
        membre.numero = instance.numero_membre
        membre.nom = instance.last_name or instance.username
        membre.prenom = instance.first_name or ''
        if instance.titre_id:
            membre.titre_id = instance.titre_id
        if instance.photo:
            membre.photo = instance.photo
        membre.actif = instance.is_active
        if instance.date_inscription:
            membre.date_inscription = instance.date_inscription
        membre.email_public = instance.email_public
        membre.telephone_public = instance.telephone_public
        membre.save()

        # Link back without re-triggering this signal
        if instance.membre_actif_id != membre.pk:
            sender.objects.filter(pk=instance.pk).update(membre_actif_id=membre.pk)

        # Manage the "Membres Actifs" group
        _sync_groupe_membres(instance)

    finally:
        _syncing_users.discard(instance.pk)


def _sync_groupe_membres(user):
    """Add/remove user from 'Membres Actifs' group based on is_active + numero_membre."""
    try:
        from django.contrib.auth.models import Group
        groupe, _ = Group.objects.get_or_create(name='Membres Actifs')
        if user.is_active and user.numero_membre:
            user.groups.add(groupe)
        else:
            user.groups.remove(groupe)
    except Exception:
        pass
