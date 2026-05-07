# src/apps/members/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.conf import settings
from django.http import HttpResponse, FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import User, Cotisation, Opportunite, DocumentMembre, ForumCategorie, ForumSujet, ForumReponse
from .forms import InscriptionForm, ConnexionForm, ProfilForm, CotisationProofForm, NouveauSujetForm, ReponseForumForm
from apps.core.models import MembreActif, Certification

# ==================== AUTHENTIFICATION ====================

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            numero_membre = form.cleaned_data['numero_membre']
            try:
                membre = MembreActif.objects.get(numero=numero_membre, actif=True)
            except MembreActif.DoesNotExist:
                form.add_error('numero_membre', "Numéro de membre invalide.")
                return render(request, 'members/inscription.html', {'form': form})

            if hasattr(membre, 'user_account') and membre.user_account:
                form.add_error('numero_membre', "Ce numéro de membre est déjà associé à un compte.")
                return render(request, 'members/inscription.html', {'form': form})

            token = get_random_string(50)
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=membre.prenom,
                last_name=membre.nom,
                membre_actif=membre,
                email_verification_token=token,
            )
            user.save()

            verify_url = f"{settings.SITE_URL}/membres/verify/{token}/"
            from .tasks import envoyer_email_verification
            envoyer_email_verification.delay(user.pk, verify_url)
            messages.success(request, "Compte créé ! Consultez votre email pour activer votre compte.")
            return redirect('members:connexion')
    else:
        form = InscriptionForm()

    return render(request, 'members/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('members:dashboard')

    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                if not user.email_verified:
                    messages.warning(request, "Veuillez vérifier votre email avant de vous connecter.")
                    return render(request, 'members/connexion.html', {'form': form})
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name()} !")
                return redirect('members:dashboard')
            else:
                messages.error(request, "Identifiants incorrects.")
    else:
        form = ConnexionForm()

    return render(request, 'members/connexion.html', {'form': form})


def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token, email_verified=False)
    except User.DoesNotExist:
        messages.error(request, "Lien de vérification invalide ou déjà utilisé.")
        return redirect('members:connexion')

    user.email_verified = True
    user.email_verification_token = ''
    user.save(update_fields=['email_verified', 'email_verification_token'])
    from .tasks import envoyer_email_bienvenue
    envoyer_email_bienvenue.delay(user.pk)
    messages.success(request, "Email vérifié ! Vous pouvez maintenant vous connecter.")
    return redirect('members:connexion')


@login_required
def deconnexion(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('core:home')


# ==================== ESPACE MEMBRE ====================

@login_required
def dashboard(request):
    """Dashboard principal"""
    user = request.user
    
    # Dernière cotisation
    derniere_cotisation = user.cotisations.order_by('-date_fin').first()
    
    # Opportunités récentes
    opportunites = Opportunite.objects.filter(publiee=True).order_by('-date_creation')[:3]
    
    # Documents récents
    documents = DocumentMembre.objects.order_by('-date_ajout')[:3]
    
    context = {
        'derniere_cotisation': derniere_cotisation,
        'opportunites': opportunites,
        'documents': documents,
        'has_certification': user.has_valid_certification,
    }
    return render(request, 'members/dashboard.html', context)


@login_required
def mon_profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour !")
            return redirect('members:mon_profil')
    else:
        form = ProfilForm(instance=request.user)

    return render(request, 'members/profil.html', {'form': form})


@login_required
def mes_cotisations(request):
    if request.method == 'POST':
        form = CotisationProofForm(request.POST, request.FILES)
        if form.is_valid():
            cotisation = get_object_or_404(
                Cotisation, id=form.cleaned_data['cotisation_id'], user=request.user
            )
            cotisation.preuve_paiement = form.cleaned_data['preuve_paiement']
            cotisation.reference_paiement = form.cleaned_data.get('reference', '')
            cotisation.methode_paiement = cotisation.methode_paiement or 'virement'
            cotisation.save()
            from .tasks import notifier_admin_preuve_cotisation
            notifier_admin_preuve_cotisation.delay(cotisation.pk)
            messages.success(request, "Preuve de paiement soumise.")
            return redirect('members:mes_cotisations')
    else:
        form = CotisationProofForm()

    cotisations = request.user.cotisations.all()
    return render(request, 'members/cotisations.html', {'cotisations': cotisations, 'form': form})


@login_required
def opportunites(request):
    """Liste des opportunités"""
    type_filter = request.GET.get('type')
    
    opportunites = Opportunite.objects.filter(publiee=True)
    
    if type_filter:
        opportunites = opportunites.filter(type_opportunite=type_filter)
    
    opportunites = opportunites.order_by('-date_creation')
    
    return render(request, 'members/opportunites.html', {
        'opportunites': opportunites,
        'type_filter': type_filter
    })


@login_required
def documents(request):
    """Documents membres"""
    categorie_filter = request.GET.get('categorie')
    
    documents = DocumentMembre.objects.all()
    
    if categorie_filter:
        documents = documents.filter(categorie=categorie_filter)
    
    documents = documents.order_by('-date_ajout')
    
    return render(request, 'members/documents.html', {
        'documents': documents,
        'categories': DocumentMembre.CATEGORIE_CHOICES,
        'categorie_filter': categorie_filter
    })


# ==================== CERTIFICAT PDF ====================

@login_required
def mon_certificat(request):
    """Affiche le certificat du membre ou permet de le télécharger"""
    if not request.user.membre_actif:
        messages.error(request, "Aucun membre actif associé à votre compte.")
        return redirect('members:dashboard')
    
    certification = request.user.latest_certification
    
    if not certification:
        messages.error(request, "Vous n'avez pas de certification valide.")
        return redirect('members:dashboard')
    
    # Si demande de téléchargement
    if request.GET.get('download') == '1':
        return generer_certificat_pdf(request.user, certification)
    
    # Sinon, afficher la page avec aperçu
    return render(request, 'members/mon_certificat.html', {
        'certification': certification
    })


def generer_certificat_pdf(user, certification):
    """Génère le PDF du certificat avec QR code"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header - Logo et titre
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 100, "CNIAH")
    
    p.setFont("Helvetica", 14)
    p.drawCentredString(width/2, height - 130, "Collège National des Ingénieurs et Architectes Haïtiens")
    
    # Ligne de séparation
    p.line(50, height - 150, width - 50, height - 150)
    
    # Titre du certificat
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width/2, height - 200, "CERTIFICAT PROFESSIONNEL")
    
    # Informations du membre
    y_position = height - 260
    p.setFont("Helvetica-Bold", 12)
    
    p.drawString(100, y_position, "Numéro de certificat :")
    p.setFont("Helvetica", 12)
    p.drawString(280, y_position, certification.numero_certificat)
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Nom complet :")
    p.setFont("Helvetica", 12)
    p.drawString(280, y_position, user.get_full_name())
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Numéro de membre :")
    p.setFont("Helvetica", 12)
    p.drawString(280, y_position, user.membre_actif.numero)
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Titre professionnel :")
    p.setFont("Helvetica", 12)
    p.drawString(280, y_position, str(user.membre_actif.titre))
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Date de délivrance :")
    p.setFont("Helvetica", 12)
    p.drawString(280, y_position, certification.date_delivrance.strftime('%d/%m/%Y'))
    
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Date d'expiration :")
    p.setFont("Helvetica", 12)
    p.drawString(280, y_position, certification.date_expiration.strftime('%d/%m/%Y'))
    
    # Statut
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y_position, "Statut :")
    if certification.est_valide:
        p.setFillColorRGB(0, 0.5, 0)  # Vert
        p.drawString(280, y_position, "VALIDE")
    else:
        p.setFillColorRGB(0.8, 0, 0)  # Rouge
        p.drawString(280, y_position, "EXPIRÉ")
    
    p.setFillColorRGB(0, 0, 0)  # Reset noir
    
    # QR Code — utilise l'image stockée, régénère si absente
    if certification.qr_code:
        qr_buffer = certification.qr_code.open('rb')
    else:
        certification.generate_qr_code()
        certification.save(update_fields=['qr_code'])
        qr_buffer = certification.qr_code.open('rb')

    # Ajouter QR code au PDF
    p.drawImage(qr_buffer, width - 200, 100, width=150, height=150)
    
    # Note en bas
    p.setFont("Helvetica", 9)
    p.drawCentredString(width/2, 80, "Scanner le QR code pour vérifier l'authenticité de ce certificat")
    
    # Pied de page
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width/2, 50, "14, Rue Capois, #3, Champs-de-Mars, Port-au-Prince, Haiti")
    p.drawCentredString(width/2, 35, "(509) 2942-3015 / (509) 2942-3016 - cniah.secretariat@gmail.com")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    response = FileResponse(buffer, as_attachment=True, filename=f'certificat_{certification.numero_certificat}.pdf')
    return response


# ==================== PAIEMENT EN LIGNE ====================

@login_required
def initier_paiement_cotisation(request, cotisation_id):
    """Redirige le membre vers MonCash ou NatCash via Plopplop."""
    from .services.plopplop_service import PlopplopService
    from .services.cotisation_service import CotisationService

    cotisation = get_object_or_404(Cotisation, pk=cotisation_id, user=request.user)

    if cotisation.statut == 'payee':
        messages.warning(request, "Cette cotisation est déjà payée.")
        return redirect('members:mes_cotisations')

    methode = request.POST.get('methode', '')
    if methode not in ('moncash', 'natcash'):
        messages.error(request, "Méthode de paiement invalide.")
        return redirect('members:mes_cotisations')

    plopplop = PlopplopService()
    if not plopplop.is_configured():
        messages.error(request, "Le paiement en ligne n'est pas encore configuré. Veuillez contacter le secrétariat.")
        return redirect('members:mes_cotisations')

    # Génère une référence unique et la stocke dans cotisation.reference_plopplop
    ref = CotisationService.initier_paiement_online(cotisation, methode)

    # Mémoriser la référence en session pour la page de retour
    request.session['cotisation_paiement_ref'] = ref

    try:
        result = plopplop.initier_paiement(
            cotisation_ref=ref,
            montant=float(cotisation.montant),
            methode=methode,
        )
    except Exception as e:
        messages.error(request, f"Service de paiement indisponible : {e}")
        return redirect('members:mes_cotisations')

    return redirect(result['redirect_url'])


@login_required
def retour_paiement_cotisation(request):
    """Page de retour après paiement Plopplop. Vérifie et valide la cotisation."""
    from .services.plopplop_service import PlopplopService
    from .services.cotisation_service import CotisationService
    from .tasks import notifier_cotisation_validee

    # Récupérer la référence depuis la session (stockée avant la redirection Plopplop)
    cotisation_ref = request.session.pop('cotisation_paiement_ref', None)
    if not cotisation_ref:
        messages.error(request, "Session expirée ou référence de paiement manquante.")
        return redirect('members:mes_cotisations')

    try:
        cotisation = Cotisation.objects.get(pk=int(cotisation_ref), user=request.user)
    except (Cotisation.DoesNotExist, ValueError):
        messages.error(request, "Cotisation introuvable.")
        return redirect('members:mes_cotisations')

    if cotisation.statut == 'payee':
        return render(request, 'members/paiement_retour.html', {
            'cotisation': cotisation,
            'confirme': True,
        })

    plopplop = PlopplopService()
    confirme = False
    try:
        result = plopplop.verifier_paiement(cotisation_ref)
        if result.get('trans_status') == 'ok':
            id_transaction = result.get('id_transaction', '')
            CotisationService.confirmer_paiement(cotisation, id_transaction)
            notifier_cotisation_validee.delay(cotisation.pk)
            confirme = True
    except Exception:
        pass

    return render(request, 'members/paiement_retour.html', {
        'cotisation': cotisation,
        'confirme': confirme,
    })


# ==================== FORUM ====================

@login_required
def forum(request):
    """Forum principal"""
    categories = ForumCategorie.objects.all()
    return render(request, 'members/forum.html', {'categories': categories})


@login_required
def forum_categorie(request, categorie_id):
    """Sujets d'une catégorie"""
    categorie = get_object_or_404(ForumCategorie, id=categorie_id)
    sujets = categorie.sujets.all()
    
    return render(request, 'members/forum_categorie.html', {
        'categorie': categorie,
        'sujets': sujets
    })


@login_required
def forum_sujet(request, sujet_id):
    sujet = get_object_or_404(ForumSujet, id=sujet_id)
    ForumSujet.objects.filter(pk=sujet.pk).update(vues=sujet.vues + 1)

    if request.method == 'POST':
        form = ReponseForumForm(request.POST)
        if form.is_valid():
            ForumReponse.objects.create(
                sujet=sujet,
                auteur=request.user,
                contenu=form.cleaned_data['contenu'],
            )
            messages.success(request, "Réponse publiée !")
            return redirect('members:forum_sujet', sujet_id=sujet.id)
    else:
        form = ReponseForumForm()

    reponses = sujet.reponses.select_related('auteur').all()
    return render(request, 'members/forum_sujet.html', {
        'sujet': sujet,
        'reponses': reponses,
        'form': form,
    })


@login_required
def nouveau_sujet(request, categorie_id):
    categorie = get_object_or_404(ForumCategorie, id=categorie_id)

    if request.method == 'POST':
        form = NouveauSujetForm(request.POST)
        if form.is_valid():
            sujet = form.save(commit=False)
            sujet.categorie = categorie
            sujet.auteur = request.user
            sujet.save()
            messages.success(request, "Sujet créé !")
            return redirect('members:forum_sujet', sujet_id=sujet.id)
    else:
        form = NouveauSujetForm(initial={'categorie': categorie})

    return render(request, 'members/nouveau_sujet.html', {'categorie': categorie, 'form': form})