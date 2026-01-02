# src/apps/members/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.http import HttpResponse, FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
import qrcode
from .models import *
from apps.core.models import MembreActif, Certification

# ==================== AUTHENTIFICATION ====================

def inscription(request):
    """Inscription d'un nouveau membre"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        numero_membre = request.POST.get('numero_membre')
        
        # Validations
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'members/inscription.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return render(request, 'members/inscription.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'members/inscription.html')
        
        # Vérifier le numéro de membre
        try:
            membre = MembreActif.objects.get(numero=numero_membre, actif=True)
            
            if hasattr(membre, 'user_account') and membre.user_account:
                messages.error(request, "Ce numéro de membre est déjà associé à un compte.")
                return render(request, 'members/inscription.html')
            
        except MembreActif.DoesNotExist:
            messages.error(request, "Numéro de membre invalide.")
            return render(request, 'members/inscription.html')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=membre.prenom,
            last_name=membre.nom,
            membre_actif=membre
        )
        
        # Token de vérification
        token = get_random_string(50)
        user.email_verification_token = token
        user.save()
        
        messages.success(request, "Compte créé ! Vérifiez votre email.")
        return redirect('members:connexion')
    
    return render(request, 'members/inscription.html')


def connexion(request):
    """Connexion"""
    if request.user.is_authenticated:
        return redirect('members:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.email_verified:
                messages.warning(request, "Veuillez vérifier votre email.")
                return render(request, 'members/connexion.html')
            
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name()} !")
            return redirect('members:dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")
    
    return render(request, 'members/connexion.html')


@login_required
def deconnexion(request):
    """Déconnexion"""
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
    """Profil du membre"""
    if request.method == 'POST':
        user = request.user
        user.phone = request.POST.get('phone')
        user.save()
        
        messages.success(request, "Profil mis à jour !")
        return redirect('members:mon_profil')
    
    return render(request, 'members/profil.html')


@login_required
def mes_cotisations(request):
    """Gestion des cotisations"""
    if request.method == 'POST':
        cotisation_id = request.POST.get('cotisation_id')
        preuve = request.FILES.get('preuve_paiement')
        reference = request.POST.get('reference')
        
        cotisation = get_object_or_404(Cotisation, id=cotisation_id, user=request.user)
        cotisation.preuve_paiement = preuve
        cotisation.reference_paiement = reference
        cotisation.save()
        
        messages.success(request, "Preuve de paiement soumise.")
        return redirect('members:mes_cotisations')
    
    cotisations = request.user.cotisations.all()
    return render(request, 'members/cotisations.html', {'cotisations': cotisations})


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
    
    # Génération QR Code
    qr_url = f"{settings.SITE_URL}/verifier-certification/?numero={certification.numero_certificat}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
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
    """Détail d'un sujet"""
    sujet = get_object_or_404(ForumSujet, id=sujet_id)
    
    # Incrémenter vues
    sujet.vues += 1
    sujet.save()
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        ForumReponse.objects.create(
            sujet=sujet,
            auteur=request.user,
            contenu=contenu
        )
        messages.success(request, "Réponse publiée!")
        return redirect('members:forum_sujet', sujet_id=sujet.id)
    
    reponses = sujet.reponses.select_related('auteur').all()
    
    return render(request, 'members/forum_sujet.html', {
        'sujet': sujet,
        'reponses': reponses
    })


@login_required
def nouveau_sujet(request, categorie_id):
    """Créer un nouveau sujet"""
    categorie = get_object_or_404(ForumCategorie, id=categorie_id)
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        
        sujet = ForumSujet.objects.create(
            categorie=categorie,
            auteur=request.user,
            titre=titre,
            contenu=contenu
        )
        
        messages.success(request, "Sujet créé !")
        return redirect('members:forum_sujet', sujet_id=sujet.id)
    
    return render(request, 'members/nouveau_sujet.html', {'categorie': categorie})