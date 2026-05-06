from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File
from .models import Certification, Plainte


@receiver(post_save, sender=Certification)
def generer_qr_code(sender, instance, created, **kwargs):
    """Génère automatiquement le QR code à la création d'une certification."""
    if created or not instance.qr_code:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        data = f"CNIAH|{instance.numero_certificat}|{instance.membre.nom}|{instance.membre.prenom}"
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_cert_{instance.numero_certificat}.png'
        instance.qr_code.save(filename, File(buffer), save=False)
        Certification.objects.filter(pk=instance.pk).update(qr_code=instance.qr_code)


@receiver(pre_save, sender=Plainte)
def memoriser_statut_plainte(sender, instance, **kwargs):
    """Sauvegarde le statut avant modification pour détecter les changements."""
    if instance.pk:
        try:
            instance._ancien_statut = Plainte.objects.get(pk=instance.pk).statut
        except Plainte.DoesNotExist:
            instance._ancien_statut = None
    else:
        instance._ancien_statut = None


@receiver(post_save, sender=Plainte)
def notifier_statut_plainte(sender, instance, created, **kwargs):
    """Envoie une notification au plaignant quand le statut change."""
    if created:
        return
    ancien = getattr(instance, '_ancien_statut', None)
    if ancien and ancien != instance.statut:
        from apps.members.tasks import notifier_changement_statut_plainte
        notifier_changement_statut_plainte.delay(instance.pk)