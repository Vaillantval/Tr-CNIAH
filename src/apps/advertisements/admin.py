# src/apps/advertisements/admin.py
from django.contrib import admin
from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'start_date', 'end_date', 'is_active', 'clicks']
    list_filter = ['position', 'is_active', 'start_date', 'end_date']
    search_fields = ['title']
    readonly_fields = ['clicks', 'created_at', 'updated_at']

    fieldsets = (
        ('Publicité payante — espace affiché pour une période donnée', {
            'description': (
                "⚠️ Tailles d'image selon la position :\n"
                "• Bannière (haut de page) : 1200 × 300 px\n"
                "• Barre latérale : 300 × 250 px\n"
                "• Pied de page : 728 × 90 px\n"
                "Format JPG ou PNG, moins de 500 Ko."
            ),
            'fields': ('title', 'image', 'link', 'position')
        }),
        ('Dates de diffusion', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Options', {
            'fields': ('open_new_tab',)
        }),
        ('Statistiques', {
            'fields': ('clicks', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )