#src\apps\contact\models.py

from django.db import models

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'Information générale'),
        ('membership', 'Adhésion'),
        ('complaint', 'Plainte'),
        ('professional', 'Recherche de professionnel'),
        ('other', 'Autre'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='general', verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y')}"


class ProfessionalRequest(models.Model):
    PROFESSIONAL_TYPE_CHOICES = [
        ('engineer', 'Ingénieur'),
        ('architect', 'Architecte'),
        ('both', 'Les deux'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    professional_type = models.CharField(max_length=20, choices=PROFESSIONAL_TYPE_CHOICES, verbose_name="Type")
    description = models.TextField(verbose_name="Description")
    is_processed = models.BooleanField(default=False, verbose_name="Traité")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Demande de professionnel"
        verbose_name_plural = "Demandes de professionnels"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_professional_type_display()}"

