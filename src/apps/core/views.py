# src/apps/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

from .forms import AdhesionForm, PlainteForm, NewsletterForm
from .constants import COTISATION_DOCUMENT_TITRE

from apps.news.models import NewsArticle
from apps.advertisements.models import Advertisement
from apps.advertisements.models import Sponsor as AdSponsor
from .models import (
    DocumentCategory,
    ReferenceDocument,
    VideoResource,
    ImageGallery,
    MembershipDocument,
    CotisationDocument,
    FormationContent,
    CategoryFormation,
    HonneurMerite,
    PageMembresActifs,
    MembreActif,
    TitreProfessionnel,
    Certification,
    Plainte,
    DocumentPlainte,
    DocumentHistorique,
    ComiteDirection,
    MembreComite,
    CommissionApurement,
    MembreCommission,
    ConseilDiscipline,
    MembreConseil,
    Norme,
    CategoryNorme,
    Sponsor,
)


# ============= ACCUEIL =============

class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        today = now.date()

        # Actualités nationales (6 dernières publiées)
        context['national_news'] = NewsArticle.objects.filter(
            status='published',
            news_type='national',
            published_at__lte=now
        ).order_by('-published_at')[:6]

        # Actualités internationales (6 dernières publiées)
        context['international_news'] = NewsArticle.objects.filter(
            status='published',
            news_type='international',
            published_at__lte=now
        ).order_by('-published_at')[:6]

        # Articles récents (tous types, 6 derniers)
        context['recent_articles'] = NewsArticle.objects.filter(
            status='published',
            published_at__lte=now
        ).select_related('category').order_by('-published_at')[:6]

        # Publicités bannière (haut de page)
        context['banner_ads'] = Advertisement.objects.filter(
            is_active=True,
            position='banner',
            start_date__lte=today,
            end_date__gte=today
        )

        # Publicités sidebar
        context['sidebar_ads'] = Advertisement.objects.filter(
            is_active=True,
            position='sidebar',
            start_date__lte=today,
            end_date__gte=today
        )[:4]

        # Sponsors actifs — depuis apps.advertisements (is_active, order)
        context['sponsors'] = AdSponsor.objects.filter(is_active=True).order_by('order')

        return context


# ============= VUES PUBLIQUES =============

class PublicServiceView(TemplateView):
    template_name = 'pages/public/index.html'


class EngineersArchitectsView(TemplateView):
    template_name = 'pages/ingenieurs/index.html'


@login_required
def members_dashboard(request):
    return redirect('members:dashboard')


# ============= NEWSLETTER =============

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Merci de vous être abonné à notre newsletter !')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return redirect('core:home')


# ============= DOCUMENTS =============

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
        context['video_series'] = VideoResource.objects.filter(
            is_active=True,
            series_name__icontains='ZAFE GOUDOUGOUDOU'
        ).order_by('episode_number')

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

        # Catégorie courante
        context['current_category'] = category_slug
        if category_slug:
            try:
                context['current_category_obj'] = DocumentCategory.objects.get(slug=category_slug)
            except DocumentCategory.DoesNotExist:
                pass

        return context


def document_download(request, slug):
    """Télécharger un document et incrémenter le compteur"""
    document = get_object_or_404(ReferenceDocument, slug=slug, is_active=True)
    document.increment_download()
    try:
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
    except FileNotFoundError:
        raise Http404("Document non trouvé")


# ============= VIDÉOS =============

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
            related_videos = related_videos.filter(series_name=self.object.series_name)
        elif self.object.category:
            related_videos = related_videos.filter(category=self.object.category)

        context['related_videos'] = related_videos[:4]
        return context


# ============= GALERIE =============

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


# ============= ADHÉSION =============

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
    """Télécharger un document d'adhésion"""
    document = get_object_or_404(MembershipDocument, pk=pk, is_active=True)
    document.increment_download()
    try:
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )
    except FileNotFoundError:
        raise Http404("Document non trouvé")


def adhesion_view(request):
    if request.user.is_authenticated:
        return redirect('core:members_dashboard')

    if request.method == 'POST':
        form = AdhesionForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                demande = form.save()
            messages.success(
                request,
                f"Votre demande d'adhésion a été soumise avec succès ! "
                f"Le secrétariat du CNIAH vous contactera à {demande.email} dans les meilleurs délais."
            )
            return redirect('core:adhesion')
    else:
        form = AdhesionForm()

    return render(request, 'pages/cniah/adhesion.html', {'form': form})


# ============= COTISATION =============

def cotisation(request):
    """Page Cotisation et Contribution"""
    document = CotisationDocument.objects.filter(
        titre__icontains=COTISATION_DOCUMENT_TITRE,
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

    formations = formations.order_by('-date_formation', 'ordre').prefetch_related('images')

    categories = CategoryFormation.objects.all().order_by('ordre')

    context = {
        'formations': formations,
        'categories': categories,
        'categorie_filter': categorie_filter
    }
    return render(request, 'pages/cniah/formation_continue.html', context)


# ============= HONNEUR ET MÉRITE =============

def honneur_merite(request):
    """Page Honneur et Mérite"""
    honneurs = HonneurMerite.objects.all().prefetch_related('images').order_by('-annee', 'ordre')

    context = {
        'honneurs': honneurs
    }
    return render(request, 'pages/cniah/honneur_merite.html', context)


# ============= MEMBRES ACTIFS =============

def membres_actifs(request):
    """Liste des Membres Actifs avec pagination et filtres"""
    titre_filter = request.GET.get('titre', None)
    search = request.GET.get('search', '')

    # Configuration de la page
    page_config = PageMembresActifs.objects.first()

    # Membres actifs
    membres = MembreActif.objects.filter(actif=True).select_related('titre')

    if titre_filter:
        membres = membres.filter(titre_id=titre_filter)

    if search:
        membres = membres.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(numero__icontains=search)
        )

    membres = membres.order_by('nom', 'prenom')

    # Pagination
    paginator = Paginator(membres, 50)
    page_number = request.GET.get('page')
    membres_page = paginator.get_page(page_number)

    # Titres pour le filtre
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


# ============= VÉRIFIER CERTIFICATION =============

def verifier_certification(request):
    """Page Vérifier une Certification"""
    resultat = None
    methode = request.GET.get('methode', 'numero')

    if request.method == 'POST':
        methode = request.POST.get('methode', 'numero')

        if methode == 'numero':
            numero = request.POST.get('numero_certificat', '').strip()
            try:
                cert = Certification.objects.select_related(
                    'membre', 'membre__titre'
                ).get(numero_certificat=numero)
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


# ============= DÉPOSER PLAINTE =============

def deposer_plainte(request):
    if request.method == 'POST':
        form = PlainteForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                plainte = form.save()
                for file in request.FILES.getlist('documents'):
                    from .validators import validate_upload
                    try:
                        validate_upload(file)
                    except Exception:
                        continue
                    DocumentPlainte.objects.create(
                        plainte=plainte,
                        fichier=file,
                        nom_fichier=file.name,
                    )
            messages.success(
                request,
                f'Votre plainte a été enregistrée. Numéro de référence : {plainte.numero_reference}'
            )
            return redirect('core:plainte_success', numero=plainte.numero_reference)
    else:
        form = PlainteForm()

    return render(request, 'pages/cniah/deposer_plainte.html', {'form': form})


def plainte_success(request, numero):
    """Page de confirmation après dépôt de plainte"""
    plainte = get_object_or_404(Plainte, numero_reference=numero)
    context = {
        'plainte': plainte
    }
    return render(request, 'pages/cniah/plainte_success.html', context)


# ============= ABOUT =============

def about(request):
    """Page À propos du CNIAH"""

    # Documents historiques
    documents_historiques = DocumentHistorique.objects.all().order_by('ordre')

    # Comités de direction
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


# ============= NORMES =============

def norms(request):
    """Page Normes avec catégories et filtres"""
    categorie_filter = request.GET.get('categorie', None)
    search = request.GET.get('search', '')

    normes = Norme.objects.filter(actif=True).select_related('categorie')

    if categorie_filter:
        normes = normes.filter(categorie_id=categorie_filter)

    if search:
        normes = normes.filter(
            Q(titre__icontains=search) |
            Q(description__icontains=search) |
            Q(version__icontains=search)
        )

    normes = normes.order_by('-date_publication')
    categories = CategoryNorme.objects.all().order_by('ordre')

    context = {
        'normes': normes,
        'categories': categories,
        'categorie_filter': categorie_filter,
        'search': search,
        'total_normes': normes.count()
    }
    return render(request, 'pages/cniah/norms.html', context)


# ============= SPONSORS =============

def sponsors(request):
    """Page Sponsors"""
    context = {
        'sponsors_platine': Sponsor.objects.filter(niveau='platine', actif=True).order_by('ordre'),
        'sponsors_or':      Sponsor.objects.filter(niveau='or',      actif=True).order_by('ordre'),
        'sponsors_argent':  Sponsor.objects.filter(niveau='argent',  actif=True).order_by('ordre'),
        'sponsors_bronze':  Sponsor.objects.filter(niveau='bronze',  actif=True).order_by('ordre'),
        'total_sponsors':   Sponsor.objects.filter(actif=True).count(),
    }
    return render(request, 'pages/cniah/sponsors.html', context)


# ============= ADVERTISING =============

def advertising(request):
    """Page Publicité"""
    context = {}
    return render(request, 'pages/cniah/advertising.html', context)