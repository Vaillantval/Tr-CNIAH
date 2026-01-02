# src/apps/core/context_processors.py
from django.utils import timezone
from apps.advertisements.models import Advertisement


def global_ads(request):
    """Context processor pour rendre les publicités disponibles partout"""
    today = timezone.now().date()
    
    return {
        'footer_ads': Advertisement.objects.filter(
            is_active=True,
            position='footer',
            start_date__lte=today,
            end_date__gte=today
        )[:3]
    }