from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File
from .models import Certification

@receiver(post_save, sender=Certification)
def generer_qr_code(sender, instance, created, **kwargs):
    """
    Génère automatiquement un QR code pour chaque nouvelle certification.
    Le QR code contient le numéro de certificat pour vérification rapide.
    """
    if created or not instance.qr_code:
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Données à encoder dans le QR code
        # Format: CNIAH|NUMERO_CERT|NOM|PRENOM
        data = f"CNIAH|{instance.numero_certificat}|{instance.membre.nom}|{instance.membre.prenom}"
        qr.add_data(data)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder dans un buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Générer le nom du fichier
        filename = f'qr_cert_{instance.numero_certificat}.png'
        
        # Sauvegarder le fichier dans le modèle
        instance.qr_code.save(filename, File(buffer), save=False)
        
        # Sauvegarder sans déclencher le signal à nouveau
        Certification.objects.filter(pk=instance.pk).update(qr_code=instance.qr_code)