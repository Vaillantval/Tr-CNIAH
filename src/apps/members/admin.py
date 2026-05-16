# src/apps/members/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    User, Cotisation, PaiementCertificat, Don,
    Opportunite, DocumentMembre,
    ForumCategorie, ForumSujet, ForumReponse,
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'membre_actif', 'email_verified', 'is_active', 'changer_mdp_lien']
    list_filter = ['email_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    actions = ['definir_mot_de_passe_temporaire', 'activer_compte', 'desactiver_compte', 'envoyer_email_init_password']

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
        }),
    ) + BaseUserAdmin.fieldsets[1:] + (
        ('Informations CNIAH', {
            'fields': ('membre_actif', 'email_verified', 'phone')
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = "Nom complet"

    def changer_mdp_lien(self, obj):
        url = reverse('admin:members_user_password_change', args=[obj.pk])
        return format_html('<a href="{}" class="button">Changer mdp</a>', url)
    changer_mdp_lien.short_description = "Mot de passe"

    @admin.action(description="🔑 Définir un mot de passe temporaire et activer le compte")
    def definir_mot_de_passe_temporaire(self, request, queryset):
        import secrets
        from django.contrib import messages as django_messages
        lines = []
        for user in queryset:
            # Build a readable temporary password
            suffix = secrets.token_hex(3).upper()  # 6 hex chars, e.g. A3F9C1
            temp_pwd = f"Cniah@{suffix}"
            user.set_password(temp_pwd)
            user.is_active = True
            user.email_verified = True
            user.save()
            lines.append(f"{user.get_full_name()} ({user.username})  →  {temp_pwd}")
        summary = "  |  ".join(lines)
        self.message_user(
            request,
            f"Mots de passe temporaires définis — communiquez-les aux membres : {summary}",
            level=django_messages.WARNING,
        )

    @admin.action(description="Activer le compte (email vérifié + compte actif)")
    def activer_compte(self, request, queryset):
        updated = queryset.update(email_verified=True, is_active=True)
        self.message_user(request, f"{updated} compte(s) activé(s).")

    @admin.action(description="Désactiver le compte")
    def desactiver_compte(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} compte(s) désactivé(s).")

    @admin.action(description="Envoyer email d'initialisation du mot de passe")
    def envoyer_email_init_password(self, request, queryset):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.conf import settings
        from .tasks import envoyer_email_initialisation_mot_de_passe
        sent = 0
        skipped = 0
        for user in queryset:
            if not user.email:
                skipped += 1
                continue
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.SITE_URL}/membres/password-reset/{uid}/{token}/"
            # Activate the account so the reset link works
            user.is_active = True
            user.email_verified = True
            user.save(update_fields=['is_active', 'email_verified'])
            envoyer_email_initialisation_mot_de_passe.delay(user.pk, reset_url)
            sent += 1
        msg = f"Email d'initialisation envoyé à {sent} utilisateur(s)."
        if skipped:
            msg += f" {skipped} ignoré(s) (pas d'email)."
        self.message_user(request, msg)


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'montant', 'date_debut', 'date_fin',
        'statut', 'methode_paiement', 'reference_paiement', 'date_paiement',
    ]
    list_filter = ['statut', 'methode_paiement', 'date_debut', 'date_fin']
    search_fields = ['user__username', 'user__email', 'reference_paiement', 'reference_plopplop']
    date_hierarchy = 'date_debut'
    readonly_fields = ['date_paiement', 'reference_plopplop', 'methode_paiement']
    
    actions = ['valider_paiement']
    
    @admin.action(description="Valider le paiement")
    def valider_paiement(self, request, queryset):
        from django.utils import timezone
        from .tasks import notifier_cotisation_validee
        ids = list(queryset.values_list('pk', flat=True))
        queryset.update(statut='payee', date_paiement=timezone.now())
        for pk in ids:
            notifier_cotisation_validee.delay(pk)
        self.message_user(request, f"{len(ids)} cotisation(s) validée(s).")


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

@admin.register(PaiementCertificat)
class PaiementCertificatAdmin(admin.ModelAdmin):
    list_display = ['user', 'montant', 'devise', 'annees_payees', 'statut', 'methode_paiement', 'date_creation']
    list_filter = ['statut', 'devise', 'methode_paiement', 'date_creation']
    search_fields = ['user__username', 'user__email', 'reference_paiement']
    readonly_fields = ['date_creation']
    date_hierarchy = 'date_creation'

    actions = ['valider_paiement']

    @admin.action(description="Valider le paiement")
    def valider_paiement(self, request, queryset):
        from django.utils import timezone
        from .tasks import confirmer_paiement_certificat
        ids = list(queryset.values_list('pk', flat=True))
        queryset.update(statut='valide', date_paiement=timezone.now())
        for pk in ids:
            confirmer_paiement_certificat.delay(pk)
        self.message_user(request, f"{len(ids)} paiement(s) de certification validé(s).")


@admin.register(Don)
class DonAdmin(admin.ModelAdmin):
    list_display = ['get_donateur', 'montant', 'devise', 'statut', 'methode_paiement', 'date_don']
    list_filter = ['statut', 'devise', 'methode_paiement', 'date_don']
    search_fields = ['nom_donateur', 'email_donateur', 'user__username', 'reference_paiement']
    readonly_fields = ['date_don']
    date_hierarchy = 'date_don'

    actions = ['confirmer_don']

    def get_donateur(self, obj):
        return obj.nom_donateur or (obj.user.get_full_name() if obj.user else 'Anonyme')
    get_donateur.short_description = "Donateur"

    @admin.action(description="Confirmer le don reçu")
    def confirmer_don(self, request, queryset):
        from .tasks import confirmer_reception_don
        ids = list(queryset.values_list('pk', flat=True))
        queryset.update(statut='confirme')
        for pk in ids:
            confirmer_reception_don.delay(pk)
        self.message_user(request, f"{len(ids)} don(s) confirmé(s).")
