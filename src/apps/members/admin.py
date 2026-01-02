# src/apps/members/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'membre_actif', 'email_verified', 'is_active']
    list_filter = ['email_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations CNIAH', {
            'fields': ('membre_actif', 'email_verified', 'phone')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = "Nom complet"


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ['user', 'montant', 'date_debut', 'date_fin', 'statut', 'date_paiement']
    list_filter = ['statut', 'date_debut', 'date_fin']
    search_fields = ['user__username', 'user__email', 'reference_paiement']
    date_hierarchy = 'date_debut'
    readonly_fields = ['date_paiement']
    
    actions = ['valider_paiement']
    
    @admin.action(description="Valider le paiement")
    def valider_paiement(self, request, queryset):
        from django.utils import timezone
        queryset.update(statut='payee', date_paiement=timezone.now())
        self.message_user(request, f"{queryset.count()} cotisation(s) validée(s).")


@admin.register(Opportunite)
class OpportuniteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_opportunite', 'entreprise', 'localisation', 'date_limite', 'publiee']
    list_filter = ['type_opportunite', 'publiee', 'date_creation']
    search_fields = ['titre', 'entreprise', 'description']
    date_hierarchy = 'date_creation'
    list_editable = ['publiee']


@admin.register(DocumentMembre)
class DocumentMembreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'date_ajout']
    list_filter = ['categorie', 'date_ajout']
    search_fields = ['titre', 'description']


@admin.register(ForumCategorie)
class ForumCategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre']
    list_editable = ['ordre']
    ordering = ['ordre']


@admin.register(ForumSujet)
class ForumSujetAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'categorie', 'epingle', 'verrouille', 'vues', 'date_creation']
    list_filter = ['categorie', 'epingle', 'verrouille', 'date_creation']
    search_fields = ['titre', 'contenu', 'auteur__username']
    date_hierarchy = 'date_creation'
    list_editable = ['epingle', 'verrouille']


@admin.register(ForumReponse)
class ForumReponseAdmin(admin.ModelAdmin):
    list_display = ['sujet', 'auteur', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['contenu', 'auteur__username', 'sujet__titre']
    date_hierarchy = 'date_creation'