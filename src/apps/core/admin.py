#src\apps\core\admin.py

from django.contrib import admin
from .models import *

admin.site.site_header = "Administration CNIAH"
admin.site.site_title = "CNIAH Admin"
admin.site.index_title = "Bienvenue dans l'administration du CNIAH"

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']


@admin.register(ServiceBlock)
class ServiceBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(Proposition)
class PropositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(EngineeringBranch)
class EngineeringBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'order']
    list_editable = ['is_active', 'order']


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
    list_display = ['numero', 'nom', 'prenom', 'titre', 'actif', 'date_inscription']
    list_filter = ['titre', 'actif', 'date_inscription']
    search_fields = ['numero', 'nom', 'prenom']
    list_editable = ['actif']
    ordering = ['nom', 'prenom']
    date_hierarchy = 'date_inscription'
    
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
        # Limite à une seule instance
        return not PageMembresActifs.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============= CERTIFICATION =============
@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['numero_certificat', 'membre', 'date_delivrance', 'date_expiration', 'statut', 'est_valide']
    list_filter = ['statut', 'date_delivrance', 'date_expiration']
    search_fields = ['numero_certificat', 'membre__nom', 'membre__prenom']
    date_hierarchy = 'date_delivrance'
    readonly_fields = ['qr_code']
    
    fieldsets = (
        ('Informations', {
            'fields': ('numero_certificat', 'membre', 'statut')
        }),
        ('Dates', {
            'fields': ('date_delivrance', 'date_expiration')
        }),
        ('QR Code', {
            'fields': ('qr_code',),
            'description': 'Le QR code est généré automatiquement'
        }),
    )


# ============= PLAINTES =============
class DocumentPlainteInline(admin.TabularInline):
    model = DocumentPlainte
    extra = 0
    fields = ['fichier', 'nom_fichier']


@admin.register(Plainte)
class PlainteAdmin(admin.ModelAdmin):
    list_display = ['numero_reference', 'nom_plaignant', 'membre_concerne', 'type_plainte', 'statut', 'date_soumission']
    list_filter = ['statut', 'type_plainte', 'date_soumission']
    search_fields = ['numero_reference', 'nom_plaignant', 'email_plaignant', 'membre_concerne']
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
            'fields': ('membre_concerne', 'type_plainte', 'description')
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
class MembreComiteInline(admin.TabularInline):
    model = MembreComite
    extra = 1
    fields = ['prenom', 'nom', 'poste', 'photo', 'ordre']


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
    list_display = ['nom_complet', 'poste', 'comite', 'ordre']
    list_filter = ['comite', 'poste']
    search_fields = ['nom', 'prenom']
    ordering = ['comite', 'ordre']
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = "Nom complet"


# ============= COMMISSION D'APUREMENT =============
class MembreCommissionInline(admin.TabularInline):
    model = MembreCommission
    extra = 1
    fields = ['prenom', 'nom', 'photo', 'ordre']


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
    list_display = ['nom_complet', 'commission', 'ordre']
    list_filter = ['commission']
    search_fields = ['nom', 'prenom']
    ordering = ['commission', 'ordre']
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = "Nom complet"


# ============= CONSEIL DE DISCIPLINE =============
class MembreConseilInline(admin.TabularInline):
    model = MembreConseil
    extra = 1
    fields = ['prenom', 'nom', 'photo', 'ordre']


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