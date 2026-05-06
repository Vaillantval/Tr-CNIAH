from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def envoyer_email_verification(self, user_id: int, verify_url: str):
    """Email de vérification envoyé à l'inscription."""
    from apps.members.models import User
    try:
        user = User.objects.get(pk=user_id)
        send_mail(
            subject="CNIAH — Vérification de votre adresse email",
            message=(
                f"Bonjour {user.get_full_name()},\n\n"
                f"Cliquez sur le lien suivant pour activer votre compte :\n{verify_url}\n\n"
                f"Ce lien est personnel et ne doit pas être partagé.\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def envoyer_email_bienvenue(self, user_id: int):
    """Email de bienvenue envoyé après validation de l'adresse email."""
    from apps.members.models import User
    try:
        user = User.objects.select_related('membre_actif').get(pk=user_id)
        send_mail(
            subject="Bienvenue au CNIAH — Votre compte est activé",
            message=(
                f"Bonjour {user.get_full_name()},\n\n"
                f"Votre compte CNIAH est maintenant activé. "
                f"Vous pouvez vous connecter sur {settings.SITE_URL}/membres/connexion/\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def envoyer_confirmation_adhesion(self, demande_id: int):
    """Confirmation de réception envoyée après soumission d'une demande d'adhésion."""
    from apps.core.models import DemandeAdhesion
    try:
        demande = DemandeAdhesion.objects.get(pk=demande_id)
        send_mail(
            subject="CNIAH — Demande d'adhésion reçue",
            message=(
                f"Bonjour {demande.prenom} {demande.nom},\n\n"
                f"Nous avons bien reçu votre demande d'adhésion au CNIAH. "
                f"Le secrétariat vous contactera à {demande.email} dans les meilleurs délais.\n\n"
                f"Conservez précieusement cet email comme accusé de réception.\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notifier_changement_statut_plainte(self, plainte_id: int):
    """Notification envoyée au plaignant quand le statut de sa plainte change."""
    from apps.core.models import Plainte
    try:
        plainte = Plainte.objects.get(pk=plainte_id)
        send_mail(
            subject=f"CNIAH — Mise à jour de votre plainte {plainte.numero_reference}",
            message=(
                f"Bonjour {plainte.nom_plaignant},\n\n"
                f"Le statut de votre plainte {plainte.numero_reference} a été mis à jour :\n"
                f"Nouveau statut : {plainte.get_statut_display()}\n\n"
                f"Pour toute question, contactez le secrétariat du CNIAH.\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[plainte.email_plaignant],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def envoyer_rappel_cotisation(self, user_id: int):
    """Rappel envoyé aux membres dont la cotisation est échue."""
    from apps.members.models import User
    try:
        user = User.objects.get(pk=user_id)
        send_mail(
            subject="CNIAH — Rappel de cotisation",
            message=(
                f"Bonjour {user.get_full_name()},\n\n"
                f"Nous vous rappelons que votre cotisation annuelle est arrivée à échéance. "
                f"Connectez-vous sur {settings.SITE_URL}/membres/cotisations/ pour la régler.\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
