from django.core.management.base import BaseCommand
from apps.core.models import Certification


class Command(BaseCommand):
    help = "Régénère les QR codes manquants pour toutes les certifications existantes."

    def handle(self, *args, **options):
        certifications = Certification.objects.filter(qr_code='')
        total = certifications.count()
        self.stdout.write(f"{total} certification(s) sans QR code trouvée(s).")
        for cert in certifications:
            cert.generate_qr_code()
            Certification.objects.filter(pk=cert.pk).update(qr_code=cert.qr_code)
            self.stdout.write(f"  ✓ {cert.numero_certificat}")
        self.stdout.write(self.style.SUCCESS(f"Terminé. {total} QR code(s) générés."))
