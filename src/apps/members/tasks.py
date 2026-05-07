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
def notifier_admin_nouvelle_adhesion(self, demande_id: int):
    """Alerte l'admin qu'une nouvelle demande d'adhésion vient d'être soumise."""
    from apps.core.models import DemandeAdhesion
    admin_email = settings.ADMIN_NOTIFY_EMAIL
    if not admin_email:
        return
    try:
        demande = DemandeAdhesion.objects.get(pk=demande_id)
        send_mail(
            subject=f"CNIAH — Nouvelle demande d'adhésion : {demande.prenom} {demande.nom}",
            message=(
                f"Une nouvelle demande d'adhésion a été soumise.\n\n"
                f"Candidat    : {demande.prenom} {demande.nom}\n"
                f"Email       : {demande.email}\n"
                f"Téléphone   : {demande.telephone}\n"
                f"Type        : {demande.get_type_demande_display()}\n"
                f"Statut visé : {demande.get_statut_souhaite_display()}\n"
                f"Titre       : {demande.titre}\n"
                f"Soumis le   : {demande.date_soumission.strftime('%d/%m/%Y à %H:%M')}\n\n"
                f"Consultez le dossier dans l'administration CNIAH."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_email,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notifier_admin_nouvelle_plainte(self, plainte_id: int):
    """Alerte l'admin qu'une nouvelle plainte vient d'être déposée."""
    from apps.core.models import Plainte
    admin_email = settings.ADMIN_NOTIFY_EMAIL
    if not admin_email:
        return
    try:
        plainte = Plainte.objects.get(pk=plainte_id)
        send_mail(
            subject=f"CNIAH — Nouvelle plainte : {plainte.numero_reference}",
            message=(
                f"Une nouvelle plainte a été déposée.\n\n"
                f"Référence   : {plainte.numero_reference}\n"
                f"Plaignant   : {plainte.nom_plaignant}\n"
                f"Email       : {plainte.email_plaignant}\n"
                f"Téléphone   : {plainte.telephone}\n"
                f"Type        : {plainte.get_type_plainte_display()}\n"
                f"Membre visé : {plainte.membre_concerne}\n"
                f"Soumis le   : {plainte.date_soumission.strftime('%d/%m/%Y à %H:%M')}\n\n"
                f"Consultez le dossier dans l'administration CNIAH."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_email,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notifier_admin_preuve_cotisation(self, cotisation_id: int):
    """Alerte l'admin qu'une preuve de paiement (virement/cash) a été soumise."""
    from apps.members.models import Cotisation
    admin_email = settings.ADMIN_NOTIFY_EMAIL
    if not admin_email:
        return
    try:
        cotisation = Cotisation.objects.select_related('user').get(pk=cotisation_id)
        user = cotisation.user
        send_mail(
            subject=f"CNIAH — Preuve de cotisation à valider : {user.get_full_name()}",
            message=(
                f"Un membre a soumis une preuve de paiement en attente de validation.\n\n"
                f"Membre      : {user.get_full_name()}\n"
                f"Email       : {user.email}\n"
                f"Période     : {cotisation.date_debut.strftime('%d/%m/%Y')} – "
                f"{cotisation.date_fin.strftime('%d/%m/%Y')}\n"
                f"Montant     : {cotisation.montant} USD\n"
                f"Référence   : {cotisation.reference_paiement or 'Non renseignée'}\n\n"
                f"Rendez-vous dans l'administration CNIAH pour valider ce paiement."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_email,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notifier_statut_demande_adhesion(self, demande_id: int):
    """Email envoyé au candidat quand le statut de sa demande d'adhésion change."""
    from apps.core.models import DemandeAdhesion
    try:
        demande = DemandeAdhesion.objects.get(pk=demande_id)
        statut = demande.statut_demande

        if statut == 'approuvee':
            subject = "CNIAH — Votre demande d'adhésion est approuvée"
            corps = (
                f"Bonjour {demande.prenom} {demande.nom},\n\n"
                f"Nous avons le plaisir de vous informer que votre demande d'adhésion "
                f"au CNIAH a été approuvée.\n\n"
                f"Le secrétariat vous contactera prochainement pour finaliser votre inscription "
                f"et vous communiquer les prochaines étapes.\n\n"
                f"Bienvenue au sein du Collège National des Ingénieurs et Architectes Haïtiens.\n\n"
                f"Le secrétariat du CNIAH\n"
                f"(509) 2942-3015 / (509) 2942-3016"
            )
        elif statut == 'rejetee':
            subject = "CNIAH — Décision sur votre demande d'adhésion"
            corps = (
                f"Bonjour {demande.prenom} {demande.nom},\n\n"
                f"Après examen de votre dossier, nous sommes au regret de vous informer "
                f"que votre demande d'adhésion au CNIAH n'a pas pu être retenue à ce stade.\n\n"
                f"Pour obtenir plus d'informations ou pour soumettre un dossier complété, "
                f"veuillez contacter le secrétariat du CNIAH.\n\n"
                f"Le secrétariat du CNIAH\n"
                f"(509) 2942-3015 / (509) 2942-3016"
            )
        elif statut == 'en_cours':
            subject = "CNIAH — Votre demande d'adhésion est en cours d'examen"
            corps = (
                f"Bonjour {demande.prenom} {demande.nom},\n\n"
                f"Votre demande d'adhésion au CNIAH est actuellement en cours d'examen "
                f"par notre commission.\n\n"
                f"Vous serez informé(e) dès qu'une décision sera prise. "
                f"Pour toute question, contactez le secrétariat.\n\n"
                f"Le secrétariat du CNIAH\n"
                f"(509) 2942-3015 / (509) 2942-3016"
            )
        else:
            return  # Pas d'email pour 'en_attente'

        send_mail(
            subject=subject,
            message=corps,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notifier_cotisation_validee(self, cotisation_id: int):
    """Email envoyé au membre quand sa cotisation est validée."""
    from apps.members.models import Cotisation
    try:
        cotisation = Cotisation.objects.select_related('user').get(pk=cotisation_id)
        user = cotisation.user
        send_mail(
            subject="CNIAH — Votre cotisation est confirmée",
            message=(
                f"Bonjour {user.get_full_name()},\n\n"
                f"Votre cotisation pour la période "
                f"{cotisation.date_debut.strftime('%d/%m/%Y')} – "
                f"{cotisation.date_fin.strftime('%d/%m/%Y')} "
                f"a été validée avec succès.\n\n"
                f"Montant : {cotisation.montant} USD\n"
                f"Référence : {cotisation.reference_paiement or 'N/A'}\n\n"
                f"Merci de votre fidélité au CNIAH.\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
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
                f"Votre cotisation annuelle au CNIAH est arrivée à échéance.\n\n"
                f"Vous pouvez la régler directement en ligne via :\n"
                f"  • MonCash ou NatCash (paiement immédiat)\n"
                f"  • Virement bancaire (en joignant votre preuve de paiement)\n\n"
                f"Accédez à votre espace de paiement ici :\n"
                f"{settings.SITE_URL}/membres/cotisations/\n\n"
                f"Pour toute question, contactez le secrétariat au (509) 2942-3015.\n\n"
                f"Le secrétariat du CNIAH"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
