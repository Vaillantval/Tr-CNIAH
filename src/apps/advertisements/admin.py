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
        ('Informations principales', {
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