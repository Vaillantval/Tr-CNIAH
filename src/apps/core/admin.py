#src\apps\core\admin.py

from django.contrib import admin
from django import forms
from .models import (
    Newsletter,
    DocumentCategory, ReferenceDocument, VideoResource, ImageGallery,
    MembershipDocument, CotisationDocument, FormationContent, FormationImage,
    CategoryFormation, HonneurMerite, HonneurMeriteImage,
    PageMembresActifs, MembreActif, TitreProfessionnel,
    ConfigurationCertificat, Certification, Plainte, DocumentPlainte,
    DocumentHistorique,
    ComiteDirection, MembreComite,
    CommissionApurement, MembreCommission,
    ConseilDiscipline, MembreConseil,
    CategoryNorme, Norme, Sponsor,
    DemandeAdhesion,
)

# Try to import CKEditor widget for rich-text biographies
try:
    from ckeditor_uploader.widgets import CKEditorUploadingWidget as _RichWidget
except ImportError:
    try:
        from ckeditor.widgets import CKEditorWidget as _RichWidget
    except ImportError:
        _RichWidget = None

admin.site.site_header = "Administration CNIAH"
admin.site.site_title = "CNIAH Admin"
admin.site.index_title = "Bienvenue dans l'administration du CNIAH"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_editable = ['is_active']

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'order', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'category_type', 'description')
        }),
        ('Affichage', {
            'fields': ('icon', 'order', 'is_active')
        }),
    )


@admin.register(ReferenceDocument)
class ReferenceDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'file_type', 'file_size', 'download_count', 
                    'is_featured', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_featured', 'file_type', 'category', 'created_at']
    search_fields = ['title', 'description', 'author']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['download_count', 'created_at', 'updated_at']
    list_editable = ['is_featured', 'is_active']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'category', 'description')
        }),
        ('Fichier', {
            'fields': ('file', 'file_type', 'file_size')
        }),
        ('Métadonnées', {
            'fields': ('author', 'version')
        }),
        ('Publication', {
            'fields': ('is_active', 'is_featured', 'order')
        }),
        ('Statistiques', {
            'fields': ('download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')


@admin.register(VideoResource)
class VideoResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'series_name', 'episode_number', 'video_type', 
                    'view_count', 'is_featured', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_featured', 'video_type', 'series_name', 'created_at']
    search_fields = ['title', 'series_name', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    list_editable = ['is_featured', 'is_active']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'series_name', 'episode_number', 'description')
        }),
        ('Vidéo', {
            'fields': ('video_type', 'video_url', 'video_file', 'thumbnail', 'duration')
        }),
        ('Organisation', {
            'fields': ('category',)
        }),
        ('Publication', {
            'fields': ('is_active', 'is_featured', 'order')
        }),
        ('Statistiques', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')


@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'description', 'caption']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'order']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Image', {
            'fields': ('image', 'caption')
        }),
        ('Organisation', {
            'fields': ('category', 'order', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')
    
@admin.register(MembershipDocument)
class MembershipDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'member_type', 'file_size', 'download_count', 
                    'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'member_type', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['download_count', 'created_at', 'updated_at']
    list_editable = ['is_active', 'order']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'description', 'member_type')
        }),
        ('Fichier', {
            'fields': ('file', 'file_size', 'icon')
        }),
        ('Publication', {
            'fields': ('is_active', 'order')
        }),
        ('Statistiques', {
            'fields': ('download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Calculer automatiquement la taille du fichier si non fournie
        if obj.file and not obj.file_size:
            size_bytes = obj.file.size
            if size_bytes < 1024:
                obj.file_size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                obj.file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                obj.file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        super().save_model(request, obj, form, change)


# ============= COTISATION =============
@admin.register(CotisationDocument)
class CotisationDocumentAdmin(admin.ModelAdmin):
    list_display = ['titre', 'date_ajout', 'actif']
    list_filter = ['actif', 'date_ajout']
    search_fields = ['titre']
    list_editable = ['actif']


# ============= FORMATION CONTINUE =============
class FormationImageInline(admin.TabularInline):
    model = FormationImage
    extra = 1
    fields = ['image', 'legende', 'ordre']


@admin.register(CategoryFormation)
class CategoryFormationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre']
    list_editable = ['ordre']
    ordering = ['ordre']


@admin.register(FormationContent)
class FormationContentAdmin(admin.ModelAdmin):
    list_display = ['titre', 'date_formation', 'type_contenu', 'categorie', 'actif']
    list_filter = ['type_contenu', 'categorie', 'date_formation', 'actif']
    search_fields = ['titre', 'description']
    list_editable = ['actif']
    ordering = ['-date_formation']
    inlines = [FormationImageInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'date_formation', 'categorie', 'type_contenu', 'description')
        }),
        ('Contenu', {
            'fields': ('video_url', 'fichier'),
            'description': 'Ajouter une URL vidéo OU un fichier selon le type de contenu'
        }),
        ('Paramètres', {
            'fields': ('ordre', 'actif')
        }),
    )


# ============= HONNEUR ET MERITE =============
class HonneurMeriteImageInline(admin.TabularInline):
    model = HonneurMeriteImage
    extra = 1
    fields = ['image', 'legende', 'ordre']


@admin.register(HonneurMerite)
class HonneurMeriteAdmin(admin.ModelAdmin):
    list_display = ['annee', 'titre', 'type_contenu', 'date_ajout']
    list_filter = ['annee', 'type_contenu']
    search_fields = ['titre', 'description']
    ordering = ['-annee', 'ordre']
    inlines = [HonneurMeriteImageInline]


# ============= MEMBRES ACTIFS =============
@admin.register(TitreProfessionnel)
class TitreProfessionnelAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre']
    list_editable = ['ordre']
    ordering = ['ordre']


@admin.register(MembreActif)
class MembreActifAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom', 'prenom', 'titre', 'actif', 'email_public', 'telephone_public', 'date_inscription']
    list_filter = ['titre', 'actif', 'date_inscription']
    search_fields = ['numero', 'nom', 'prenom', 'email_public']
    list_editable = ['actif']
    ordering = ['nom', 'prenom']
    date_hierarchy = 'date_inscription'

    fieldsets = (
        ('Identité', {
            'fields': ('numero', 'nom', 'prenom', 'titre', 'photo', 'date_inscription', 'actif')
        }),
        ('Contact public', {
            'fields': ('email_public', 'telephone_public'),
            'description': 'Ces informations seront affichées sur la liste publique des membres si renseignées.'
        }),
    )

    actions = ['activer_membres', 'desactiver_membres']

    @admin.action(description="Activer les membres sélectionnés")
    def activer_membres(self, request, queryset):
        queryset.update(actif=True)

    @admin.action(description="Désactiver les membres sélectionnés")
    def desactiver_membres(self, request, queryset):
        queryset.update(actif=False)


@admin.register(PageMembresActifs)
class PageMembresActifsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not PageMembresActifs.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConfigurationCertificat)
class ConfigurationCertificatAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Signataire', {
            'fields': ('nom_president', 'titre_president', 'signature_president'),
            'description': 'Charger une image PNG transparente de la signature du Président.'
        }),
        ('Visuels', {
            'fields': ('logo_organisation',)
        }),
        ('Texte de bas de page', {
            'fields': ('texte_bas_page',)
        }),
    )

    def has_add_permission(self, request):
        return not ConfigurationCertificat.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ============= CERTIFICATION =============
@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['numero_certificat', 'membre', 'annees_validite', 'date_delivrance', 'date_expiration', 'statut', 'est_valide']
    list_filter = ['statut', 'annees_validite', 'date_delivrance', 'date_expiration']
    search_fields = ['numero_certificat', 'membre__nom', 'membre__prenom']
    date_hierarchy = 'date_delivrance'
    readonly_fields = ['qr_code', 'date_expiration']

    fieldsets = (
        ('Informations', {
            'fields': ('numero_certificat', 'membre', 'statut')
        }),
        ('Validité', {
            'fields': ('date_delivrance', 'annees_validite', 'date_expiration'),
            'description': 'La date d\'expiration est calculée automatiquement (30 septembre, N années après délivrance).'
        }),
        ('QR Code', {
            'fields': ('qr_code',),
            'description': 'Le QR code est généré automatiquement'
        }),
    )

    actions = ['envoyer_certificat_email']

    @admin.action(description="Envoyer le certificat par email")
    def envoyer_certificat_email(self, request, queryset):
        from apps.members.tasks import envoyer_certificat_par_email
        count = 0
        for cert in queryset:
            envoyer_certificat_par_email.delay(cert.pk)
            count += 1
        self.message_user(request, f"{count} certificat(s) envoyé(s) par email.")


# ============= PLAINTES =============
class DocumentPlainteInline(admin.TabularInline):
    model = DocumentPlainte
    extra = 0
    fields = ['fichier', 'nom_fichier']


@admin.register(Plainte)
class PlainteAdmin(admin.ModelAdmin):
    list_display = ['numero_reference', 'nom_plaignant', 'membre_accuse', 'type_plainte', 'statut', 'date_soumission']
    list_filter = ['statut', 'type_plainte', 'date_soumission']
    search_fields = ['numero_reference', 'nom_plaignant', 'email_plaignant', 'membre_accuse__nom']
    readonly_fields = ['numero_reference', 'date_soumission']
    date_hierarchy = 'date_soumission'
    inlines = [DocumentPlainteInline]

    fieldsets = (
        ('Référence', {
            'fields': ('numero_reference', 'date_soumission')
        }),
        ('Plaignant', {
            'fields': ('nom_plaignant', 'email_plaignant', 'telephone')
        }),
        ('Plainte', {
            'fields': ('membre_accuse', 'membre_concerne', 'type_plainte', 'description'),
            'description': 'Utiliser "Membre accusé" pour les nouvelles plaintes. "Membre concerné" est conservé pour l\'historique.'
        }),
        ('Traitement', {
            'fields': ('statut', 'date_traitement', 'notes_internes')
        }),
    )


# ============= ABOUT - DOCUMENTS HISTORIQUES =============
@admin.register(DocumentHistorique)
class DocumentHistoriqueAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ordre']
    list_editable = ['ordre']
    ordering = ['ordre']


# ============= COMITE DE DIRECTION =============

class MembreComiteForm(forms.ModelForm):
    biographie = forms.CharField(
        widget=_RichWidget() if _RichWidget else forms.Textarea(attrs={'rows': 8}),
        required=False, label='Biographie',
    )
    class Meta:
        model = MembreComite
        fields = '__all__'


class MembreComiteInline(admin.StackedInline):
    model = MembreComite
    form = MembreComiteForm
    extra = 1
    fields = ['prenom', 'nom', 'poste', 'photo', 'biographie', 'ordre']


@admin.register(ComiteDirection)
class ComiteDirectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'annee_debut', 'annee_fin', 'actif']
    list_filter = ['actif']
    list_editable = ['actif']
    inlines = [MembreComiteInline]
    
    def save_model(self, request, obj, form, change):
        if obj.actif:
            # Désactiver tous les autres comités si celui-ci est marqué comme actif
            ComiteDirection.objects.exclude(pk=obj.pk).update(actif=False)
        super().save_model(request, obj, form, change)


@admin.register(MembreComite)
class MembreComiteAdmin(admin.ModelAdmin):
    form = MembreComiteForm
    list_display = ['nom_complet', 'poste', 'comite', 'ordre']
    list_filter = ['comite', 'poste']
    search_fields = ['nom', 'prenom']
    ordering = ['comite', 'ordre']
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = "Nom complet"


# ============= COMMISSION D'APUREMENT =============

class MembreCommissionForm(forms.ModelForm):
    biographie = forms.CharField(
        widget=_RichWidget() if _RichWidget else forms.Textarea(attrs={'rows': 8}),
        required=False, label='Biographie',
    )
    class Meta:
        model = MembreCommission
        fields = '__all__'


class MembreCommissionInline(admin.StackedInline):
    model = MembreCommission
    form = MembreCommissionForm
    extra = 1
    fields = ['prenom', 'nom', 'photo', 'biographie', 'ordre']


@admin.register(CommissionApurement)
class CommissionApurementAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'annee_debut', 'annee_fin', 'actif']
    list_filter = ['actif']
    list_editable = ['actif']
    inlines = [MembreCommissionInline]
    
    def save_model(self, request, obj, form, change):
        if obj.actif:
            CommissionApurement.objects.exclude(pk=obj.pk).update(actif=False)
        super().save_model(request, obj, form, change)


@admin.register(MembreCommission)
class MembreCommissionAdmin(admin.ModelAdmin):
    form = MembreCommissionForm
    list_display = ['nom_complet', 'commission', 'ordre']
    list_filter = ['commission']
    search_fields = ['nom', 'prenom']
    ordering = ['commission', 'ordre']
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = "Nom complet"


# ============= CONSEIL DE DISCIPLINE =============

class MembreConseilForm(forms.ModelForm):
    biographie = forms.CharField(
        widget=_RichWidget() if _RichWidget else forms.Textarea(attrs={'rows': 8}),
        required=False, label='Biographie',
    )
    class Meta:
        model = MembreConseil
        fields = '__all__'


class MembreConseilInline(admin.StackedInline):
    model = MembreConseil
    form = MembreConseilForm
    extra = 1
    fields = ['prenom', 'nom', 'photo', 'biographie', 'ordre']


@admin.register(ConseilDiscipline)
class ConseilDisciplineAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'annee_debut', 'annee_fin', 'actif']
    list_filter = ['actif']
    list_editable = ['actif']
    inlines = [MembreConseilInline]
    
    def save_model(self, request, obj, form, change):
        if obj.actif:
            ConseilDiscipline.objects.exclude(pk=obj.pk).update(actif=False)
        super().save_model(request, obj, form, change)


@admin.register(MembreConseil)
class MembreConseilAdmin(admin.ModelAdmin):
    form = MembreConseilForm
    list_display = ['nom_complet', 'conseil', 'ordre']
    list_filter = ['conseil']
    search_fields = ['nom', 'prenom']
    ordering = ['conseil', 'ordre']
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = "Nom complet"


# ============= NORMES =============
@admin.register(CategoryNorme)
class CategoryNormeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'icone', 'ordre']
    list_editable = ['ordre']
    ordering = ['ordre']


@admin.register(Norme)
class NormeAdmin(admin.ModelAdmin):
    list_display = ['titre', 'version', 'date_publication', 'categorie', 'actif']
    list_filter = ['categorie', 'date_publication', 'actif']
    search_fields = ['titre', 'description']
    list_editable = ['actif']
    date_hierarchy = 'date_publication'
    ordering = ['-date_publication']


# ============= SPONSORS =============
@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau', 'actif', 'ordre', 'date_ajout']
    list_filter = ['niveau', 'actif', 'date_ajout']
    search_fields = ['nom', 'description']
    list_editable = ['actif', 'ordre']
    ordering = ['niveau', 'ordre']

    fieldsets = (
        ('Partenaire institutionnel du CNIAH', {
            'description': (
                "Les sponsors sont des organisations partenaires qui soutiennent le CNIAH "
                "sur la durée, classées par niveau (Platine → Bronze). "
                "Leur logo s'affiche dans la section partenaires du site.\n\n"
                "⚠️ Taille du logo recommandée : 400 × 200 px, fond transparent (PNG).\n"
                "À distinguer des Publicités (espace pub payant avec dates de diffusion)."
            ),
            'fields': ('nom', 'niveau', 'logo', 'description', 'url_site', 'ordre', 'actif')
        }),
    )

# ============= DEMANDE D'ADHÉSION =============

@admin.register(DemandeAdhesion)
class DemandeAdhesionAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'prenom', 'email', 'titre',
        'type_demande', 'statut_demande', 'date_soumission',
    )
    list_filter = ('statut_demande', 'type_demande', 'statut_souhaite')
    search_fields = ('nom', 'prenom', 'email', 'telephone')
    readonly_fields = ('date_soumission',)
    list_editable = ('statut_demande',)
    date_hierarchy = 'date_soumission'

    fieldsets = (
        ('Informations de la demande', {
            'fields': ('type_demande', 'statut_demande', 'statut_souhaite', 'date_soumission'),
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'titre', 'fonction', 'nif', 'telephone', 'email', 'adresse'),
        }),
        ('Formation', {
            'fields': ('diplome_1', 'diplome_2', 'cv_resume'),
        }),
        ('Cotisations', {
            'fields': ('don_montant',),
        }),
        ('Pièces jointes', {
            'fields': (
                'photo_identite', 'copie_diplomes', 'piece_identite',
                'cv_fichier', 'certificat_cniah', 'lettre_support',
                'permis_sejour', 'autres_documents',
            ),
            'classes': ('collapse',),
        }),
        ('Notes administratives', {
            'fields': ('notes_admin',),
            'classes': ('collapse',),
        }),
    )