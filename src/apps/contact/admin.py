#src\apps\contact\admin.py

from django.contrib import admin
from .models import ContactMessage, ProfessionalRequest


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'subject', 'created_at']
    list_editable = ['is_read']
    readonly_fields = ['created_at']


@admin.register(ProfessionalRequest)
class ProfessionalRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'professional_type', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'professional_type', 'created_at']
    list_editable = ['is_processed']
    readonly_fields = ['created_at']