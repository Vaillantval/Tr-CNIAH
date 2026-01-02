# src/apps/core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.utils import timezone
from apps.news.models import NewsArticle
from apps.advertisements.models import Sponsor, Advertisement
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import *

class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hero Banner (à créer dans votre modèle)
        # context['hero_banner'] = HeroBanner.objects.filter(is_active=True).first()
        
        # Actualités nationales (6 dernières)
        context['national_news'] = NewsArticle.objects.filter(
            is_active=True,
            news_type='national',
            published_at__lte=timezone.now()
        )[:6]
        
        # Actualités internationales (6 dernières)
        context['international_news'] = NewsArticle.objects.filter(
            is_active=True,
            news_type='international',
            published_at__lte=timezone.now()
        )[:6]
        
        # Articles récents (tous types, 6 derniers)
        context['recent_articles'] = NewsArticle.objects.filter(
            is_active=True,
            published_at__lte=timezone.now()
        ).select_related('category')[:6]
        
        # Publicités
        today = timezone.now().date()
        context['banner_ads'] = Advertisement.objects.filter(
            is_active=True,
            position='banner',
            start_date__lte=today,
            end_date__gte=today
        )
        
        context['sidebar_ads'] = Advertisement.objects.filter(
            is_active=True,
            position='sidebar',
            start_date__lte=today,
            end_date__gte=today
        )[:4]
        
        # Sponsors
        context['sponsors'] = Sponsor.objects.filter(actif=True)
        
        # Service blocks (à créer dans votre modèle si nécessaire)
        # context['service_blocks'] = ServiceBlock.objects.filter(is_active=True)[:3]
        
        # Proposition document (à créer dans votre modèle si nécessaire)
        # context['proposition_document'] = PropositionDocument.objects.filter(is_active=True).first()
        
        return context


# class AboutView(TemplateView):
#     template_name = 'pages/cniah/about.html'


# class MembershipView(TemplateView):
#     template_name = 'pages/cniah/membership.html'


# class NormsView(TemplateView):
#     template_name = 'pages/cniah/norms.html'


# class SponsorsView(TemplateView):
#     template_name = 'pages/cniah/sponsors.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['sponsors'] = Sponsor.objects.filter(is_active=True)
#         return context


# class AdvertisingView(TemplateView):
#     template_name = 'pages/cniah/advertising.html'


class PublicServiceView(TemplateView):
    template_name = 'pages/public/index.html'


class EngineersArchitectsView(TemplateView):
    template_name = 'pages/ingenieurs/index.html'


class MembersDashboardView(TemplateView):
    template_name = 'members/dashboard.html'


def newsletter_subscribe(request):
    """Vue pour gérer l'inscription à la newsletter"""
    if request.method == 'POST':
        email = request.POST.get('email')
        # Logique pour enregistrer l'email dans la base de données
        # Newsletter.objects.create(email=email)
        from django.contrib import messages
        messages.success(request, 'Merci de vous être abonné à notre newsletter!')
    
    from django.shortcuts import redirect
    return redirect('core:home')

class DocumentsView(TemplateView):
    template_name = 'pages/cniah/documents.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Catégories actives
        context['categories'] = DocumentCategory.objects.filter(is_active=True)
        
        # Filtre par catégorie
        category_slug = self.request.GET.get('category')
        
        # Documents
        documents_qs = ReferenceDocument.objects.filter(is_active=True)
        if category_slug:
            documents_qs = documents_qs.filter(category__slug=category_slug)
        context['documents'] = documents_qs.select_related('category')
        
        # Vidéos (série ZAFE GOUDOUGOUDOU)
        videos_qs = VideoResource.objects.filter(
            is_active=True,
            series_name__icontains='ZAFE GOUDOUGOUDOU'
        ).order_by('episode_number')
        context['video_series'] = videos_qs
        
        # Toutes les vidéos
        all_videos_qs = VideoResource.objects.filter(is_active=True)
        if category_slug:
            all_videos_qs = all_videos_qs.filter(category__slug=category_slug)
        context['all_videos'] = all_videos_qs.select_related('category')
        
        # Galerie d'images
        images_qs = ImageGallery.objects.filter(is_active=True)
        if category_slug:
            images_qs = images_qs.filter(category__slug=category_slug)
        context['gallery_images'] = images_qs.select_related('category')[:12]
        
        # Catégorie actuelle
        context['current_category'] = category_slug
        if category_slug:
            try:
                context['current_category_obj'] = DocumentCategory.objects.get(
                    slug=category_slug
                )
            except DocumentCategory.DoesNotExist:
                pass
        
        return context


def document_download(request, slug):
    """Vue pour télécharger un document et incrémenter le compteur"""
    document = get_object_or_404(ReferenceDocument, slug=slug, is_active=True)
    
    # Incrémenter le compteur
    document.increment_download()
    
    # Servir le fichier
    try:
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
    except FileNotFoundError:
        raise Http404("Document non trouvé")


class VideoDetailView(DetailView):
    model = VideoResource
    template_name = 'pages/cniah/video_detail.html'
    context_object_name = 'video'
    slug_field = 'slug'
    
    def get_queryset(self):
        return VideoResource.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Incrémenter les vues
        self.object.increment_view()
        
        # Vidéos similaires (même série ou catégorie)
        related_videos = VideoResource.objects.filter(
            is_active=True
        ).exclude(id=self.object.id)
        
        if self.object.series_name:
            related_videos = related_videos.filter(
                series_name=self.object.series_name
            )
        elif self.object.category:
            related_videos = related_videos.filter(
                category=self.object.category
            )
        
        context['related_videos'] = related_videos[:4]
        
        return context


class ImageGalleryView(TemplateView):
    template_name = 'pages/cniah/gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Catégories
        context['categories'] = DocumentCategory.objects.filter(is_active=True)
        
        # Filtre
        category_slug = self.request.GET.get('category')
        
        images_qs = ImageGallery.objects.filter(is_active=True)
        if category_slug:
            images_qs = images_qs.filter(category__slug=category_slug)
        
        context['images'] = images_qs.select_related('category')
        context['current_category'] = category_slug
        
        return context
    

class MembershipView(TemplateView):
    template_name = 'pages/cniah/membership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Documents pour professionnels nationaux
        context['national_documents'] = MembershipDocument.objects.filter(
            is_active=True,
            member_type__in=['national', 'both']
        ).order_by('order')
        
        # Documents pour professionnels internationaux
        context['international_documents'] = MembershipDocument.objects.filter(
            is_active=True,
            member_type__in=['international', 'both']
        ).order_by('order')
        
        return context


def membership_document_download(request, pk):
    """Vue pour télécharger un document d'adhésion"""
    document = get_object_or_404(MembershipDocument, pk=pk, is_active=True)
    
    # Incrémenter le compteur
    document.increment_download()
    
    # Servir le fichier
    try:
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
    except FileNotFoundError:
        raise Http404("Document non trouvé")
    

#  ============= COTISATION =============
def cotisation(request):
    """Page Cotisation et Contribution"""
    document = CotisationDocument.objects.filter(
        titre__icontains="Liste des comptes bancaires",
        actif=True
    ).first()
    
    context = {
        'document': document
    }
    return render(request, 'pages/cniah/cotisation.html', context)


# ============= FORMATION CONTINUE =============
def formation_continue(request):
    """Page Formation Continue"""
    categorie_filter = request.GET.get('categorie', None)
    
    formations = FormationContent.objects.filter(actif=True).select_related('categorie')
    
    if categorie_filter:
        formations = formations.filter(categorie_id=categorie_filter)
    
    formations = formations.order_by('-date_formation', 'ordre')
    
    # Précharger les images pour les formations de type groupe_images
    formations = formations.prefetch_related('images')
    
    categories = CategoryFormation.objects.all().order_by('ordre')
    
    context = {
        'formations': formations,
        'categories': categories,
        'categorie_filter': categorie_filter
    }
    return render(request, 'pages/cniah/formation_continue.html', context)


# ============= HONNEUR ET MERITE =============
def honneur_merite(request):
    """Page Honneur et Mérite"""
    honneurs = HonneurMerite.objects.all().prefetch_related('images').order_by('-annee', 'ordre')
    
    context = {
        'honneurs': honneurs
    }
    return render(request, 'pages/cniah/honneur_merite.html', context)


# ============= MEMBRES ACTIFS =============
def membres_actifs(request):
    """Page Liste des Membres Actifs avec pagination et filtres"""
    titre_filter = request.GET.get('titre', None)
    search = request.GET.get('search', '')
    
    # Configuration de la page (titre et intro)
    page_config = PageMembresActifs.objects.first()
    
    # Récupérer les membres actifs
    membres = MembreActif.objects.filter(actif=True).select_related('titre')
    
    # Filtrer par titre professionnel
    if titre_filter:
        membres = membres.filter(titre_id=titre_filter)
    
    # Recherche par nom, prénom ou numéro
    if search:
        membres = membres.filter(
            Q(nom__icontains=search) | 
            Q(prenom__icontains=search) |
            Q(numero__icontains=search)
        )
    
    membres = membres.order_by('nom', 'prenom')
    
    # Pagination
    paginator = Paginator(membres, 50)  # 50 membres par page
    page_number = request.GET.get('page')
    membres_page = paginator.get_page(page_number)
    
    # Liste des titres pour le filtre
    titres = TitreProfessionnel.objects.all().order_by('ordre')
    
    context = {
        'page_config': page_config,
        'membres': membres_page,
        'titres': titres,
        'titre_filter': titre_filter,
        'search': search,
        'total_membres': membres.count()
    }
    return render(request, 'pages/cniah/membres_actifs.html', context)


# ============= VERIFIER CERTIFICATION =============
def verifier_certification(request):
    """Page Vérifier une Certification"""
    resultat = None
    methode = request.GET.get('methode', 'numero')
    
    if request.method == 'POST':
        methode = request.POST.get('methode', 'numero')
        
        if methode == 'numero':
            numero = request.POST.get('numero_certificat', '').strip()
            try:
                cert = Certification.objects.select_related('membre', 'membre__titre').get(
                    numero_certificat=numero
                )
                resultat = {
                    'trouve': True,
                    'valide': cert.est_valide,
                    'certification': cert
                }
            except Certification.DoesNotExist:
                resultat = {
                    'trouve': False,
                    'message': 'Aucun certificat trouvé avec ce numéro.'
                }
        
        elif methode == 'nom':
            nom = request.POST.get('nom', '').strip()
            prenom = request.POST.get('prenom', '').strip()
            
            if nom and prenom:
                try:
                    membre = MembreActif.objects.get(
                        nom__iexact=nom,
                        prenom__iexact=prenom,
                        actif=True
                    )
                    # Récupérer la certification la plus récente valide
                    cert = Certification.objects.filter(
                        membre=membre,
                        statut='valide'
                    ).order_by('-date_delivrance').first()
                    
                    if cert:
                        resultat = {
                            'trouve': True,
                            'valide': cert.est_valide,
                            'certification': cert
                        }
                    else:
                        resultat = {
                            'trouve': False,
                            'message': f'Aucune certification valide trouvée pour {prenom} {nom}.'
                        }
                except MembreActif.DoesNotExist:
                    resultat = {
                        'trouve': False,
                        'message': 'Aucun membre trouvé avec ce nom et prénom.'
                    }
            else:
                resultat = {
                    'trouve': False,
                    'message': 'Veuillez fournir le nom et le prénom.'
                }
    
    context = {
        'resultat': resultat,
        'methode': methode
    }
    return render(request, 'pages/cniah/verifier_certification.html', context)


# ============= DEPOSER PLAINTE =============
def deposer_plainte(request):
    """Page Déposer une Plainte"""
    if request.method == 'POST':
        # Créer la plainte
        plainte = Plainte(
            nom_plaignant=request.POST.get('nom'),
            email_plaignant=request.POST.get('email'),
            telephone=request.POST.get('telephone'),
            membre_concerne=request.POST.get('membre_concerne'),
            type_plainte=request.POST.get('type_plainte'),
            description=request.POST.get('description')
        )
        plainte.save()
        
        # Gérer les documents joints
        files = request.FILES.getlist('documents')
        for file in files:
            DocumentPlainte.objects.create(
                plainte=plainte,
                fichier=file,
                nom_fichier=file.name
            )
        
        messages.success(
            request, 
            f'Votre plainte a été enregistrée avec succès. Numéro de référence : {plainte.numero_reference}'
        )
        return redirect('core:plainte_success', numero=plainte.numero_reference)
    
    types_plainte = Plainte.TYPE_PLAINTE_CHOICES
    
    context = {
        'types_plainte': types_plainte
    }
    return render(request, 'pages/cniah/deposer_plainte.html', context)


def plainte_success(request, numero):
    """Page de confirmation après dépôt de plainte"""
    plainte = get_object_or_404(Plainte, numero_reference=numero)
    
    context = {
        'plainte': plainte
    }
    return render(request, 'pages/cniah/plainte_success.html', context)


# ============= ABOUT (REFONTE) =============
def about(request):
    """Page À propos du CNIAH - Refonte complète"""
    
    # Documents historiques
    documents_historiques = DocumentHistorique.objects.all().order_by('ordre')
    
    # Comités de direction (tous)
    comites = ComiteDirection.objects.all().order_by('-annee_debut')
    for comite in comites:
        comite.membres_list = MembreComite.objects.filter(
            comite=comite
        ).order_by('ordre')
    
    # Commission d'apurement actuelle
    commission_actuelle = CommissionApurement.objects.filter(actif=True).first()
    if commission_actuelle:
        commission_actuelle.membres_list = MembreCommission.objects.filter(
            commission=commission_actuelle
        ).order_by('ordre')
    
    # Conseil de discipline actuel
    conseil_actuel = ConseilDiscipline.objects.filter(actif=True).first()
    if conseil_actuel:
        conseil_actuel.membres_list = MembreConseil.objects.filter(
            conseil=conseil_actuel
        ).order_by('ordre')
    
    context = {
        'documents_historiques': documents_historiques,
        'comites': comites,
        'commission': commission_actuelle,
        'conseil': conseil_actuel
    }
    return render(request, 'pages/cniah/about.html', context)


# ============= NORMES (REFONTE) =============
def norms(request):
    """Page Normes - Refonte avec catégories et filtres"""
    categorie_filter = request.GET.get('categorie', None)
    search = request.GET.get('search', '')
    
    normes = Norme.objects.filter(actif=True).select_related('categorie')
    
    # Filtrer par catégorie
    if categorie_filter:
        normes = normes.filter(categorie_id=categorie_filter)
    
    # Recherche
    if search:
        normes = normes.filter(
            Q(titre__icontains=search) |
            Q(description__icontains=search) |
            Q(version__icontains=search)
        )
    
    normes = normes.order_by('-date_publication')
    
    # Catégories pour les filtres
    categories = CategoryNorme.objects.all().order_by('ordre')
    
    context = {
        'normes': normes,
        'categories': categories,
        'categorie_filter': categorie_filter,
        'search': search,
        'total_normes': normes.count()
    }
    return render(request, 'pages/cniah/norms.html', context)


# ============= SPONSORS (AMELIORE) =============
def sponsors(request):
    """Page Sponsors - Version améliorée"""
    sponsors_platine = Sponsor.objects.filter(niveau='platine', actif=True).order_by('ordre')
    sponsors_or = Sponsor.objects.filter(niveau='or', actif=True).order_by('ordre')
    sponsors_argent = Sponsor.objects.filter(niveau='argent', actif=True).order_by('ordre')
    sponsors_bronze = Sponsor.objects.filter(niveau='bronze', actif=True).order_by('ordre')
    
    # Stats
    total_sponsors = Sponsor.objects.filter(actif=True).count()
    
    context = {
        'sponsors_platine': sponsors_platine,
        'sponsors_or': sponsors_or,
        'sponsors_argent': sponsors_argent,
        'sponsors_bronze': sponsors_bronze,
        'total_sponsors': total_sponsors
    }
    return render(request, 'pages/cniah/sponsors.html', context)


# ============= ADVERTISING (AMELIORE) =============
def advertising(request):
    """Page Publicité - Version améliorée"""
    context = {}
    return render(request, 'pages/cniah/advertising.html', context)