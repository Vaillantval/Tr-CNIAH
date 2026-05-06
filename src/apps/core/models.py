#src\apps\core\models.py

from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
from io import BytesIO
from simple_history.models import HistoricalRecords
import qrcode
import random
import string

class Banner(models.Model):
    """Bannières hero pour la page d'accueil"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='banners/', verbose_name="Image")
    button_text = models.CharField(max_length=100, blank=True, verbose_name="Texte du bouton")
    button_link = models.CharField(max_length=200, blank=True, verbose_name="Lien du bouton")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bannière"
        verbose_name_plural = "Bannières"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class ServiceBlock(models.Model):
    """Blocs de service sur la page d'accueil"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = RichTextField(verbose_name="Description")
    button_text = models.CharField(max_length=100, blank=True, verbose_name="Texte du bouton")
    button_link = models.CharField(max_length=200, blank=True, verbose_name="Lien du bouton")
    icon = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône Material", verbose_name="Icône")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bloc de service"
        verbose_name_plural = "Blocs de service"
        ordering = ['order']

    def __str__(self):
        return self.title


class Proposition(models.Model):
    """Documents propositions du CNIAH"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    file = models.FileField(upload_to='propositions/', verbose_name="Fichier PDF")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proposition"
        verbose_name_plural = "Propositions"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class EngineeringBranch(models.Model):
    """Branches d'ingénierie et d'architecture"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=50, default='engineering', verbose_name="Icône")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Branche d'ingénierie"
        verbose_name_plural = "Branches d'ingénierie"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Newsletter(models.Model):
    """Abonnements newsletter"""
    email = models.EmailField(unique=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abonnement Newsletter"
        verbose_name_plural = "Abonnements Newsletter"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
    

class DocumentCategory(models.Model):
    """Catégories pour les documents de référence"""
    CATEGORY_CHOICES = [
        ('architecture', 'Architecture'),
        ('regulation', 'Réglementation'),
        ('technical', 'Technique'),
        ('forms', 'Formulaires'),
        ('guides', 'Guides'),
    ]
    
    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField("Slug", unique=True, blank=True)
    category_type = models.CharField("Type", max_length=20, choices=CATEGORY_CHOICES, default='technical')
    description = models.TextField("Description", blank=True)
    icon = models.CharField("Icône", max_length=50, default='library_books', 
                           help_text="Nom de l'icône Material Symbols")
    order = models.IntegerField("Ordre", default=0)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie de document"
        verbose_name_plural = "Catégories de documents"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ReferenceDocument(models.Model):
    """Documents de référence (PDF, DOCX, etc.)"""
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('doc', 'Document Word'),
        ('xls', 'Excel'),
        ('ppt', 'PowerPoint'),
        ('zip', 'Archive ZIP'),
    ]
    
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='documents'
    )
    description = models.TextField("Description")
    file = models.FileField("Fichier", upload_to='documents/%Y/%m/')
    file_type = models.CharField("Type de fichier", max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.CharField("Taille du fichier", max_length=20, blank=True, 
                                help_text="Ex: 4.2 MB")
    
    # Métadonnées
    author = models.CharField("Auteur", max_length=100, blank=True)
    version = models.CharField("Version", max_length=20, blank=True)
    
    # Publication
    is_active = models.BooleanField("Publié", default=True)
    is_featured = models.BooleanField("Mis en avant", default=False)
    order = models.IntegerField("Ordre", default=0)
    
    # Stats
    download_count = models.PositiveIntegerField("Téléchargements", default=0, editable=False)
    
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)
    
    class Meta:
        verbose_name = "Document de référence"
        verbose_name_plural = "Documents de référence"
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto-déterminer le type de fichier si non fourni
        if not self.file_type and self.file:
            ext = self.file.name.split('.')[-1].lower()
            type_map = {
                'pdf': 'pdf',
                'doc': 'doc', 'docx': 'doc',
                'xls': 'xls', 'xlsx': 'xls',
                'ppt': 'ppt', 'pptx': 'ppt',
                'zip': 'zip', 'rar': 'zip'
            }
            self.file_type = type_map.get(ext, 'pdf')
        super().save(*args, **kwargs)
    
    def get_icon_color(self):
        """Retourne la classe de couleur selon le type de fichier"""
        colors = {
            'pdf': 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400',
            'doc': 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400',
            'xls': 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400',
            'ppt': 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400',
            'zip': 'text-gray-600 bg-gray-50 dark:bg-gray-900/20 dark:text-gray-400',
        }
        return colors.get(self.file_type, colors['pdf'])
    
    def increment_download(self):
        """Incrémente le compteur de téléchargements"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class VideoResource(models.Model):
    """Ressources vidéo (YouTube, Vimeo, ou upload direct)"""
    VIDEO_TYPE_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('upload', 'Upload Direct'),
    ]
    
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    series_name = models.CharField("Nom de la série", max_length=100, blank=True,
                                  help_text="Ex: ZAFE GOUDOUGOUDOU")
    episode_number = models.PositiveIntegerField("Numéro d'épisode", null=True, blank=True)
    description = models.TextField("Description")
    
    # Vidéo
    video_type = models.CharField("Type de vidéo", max_length=20, choices=VIDEO_TYPE_CHOICES)
    video_url = models.URLField("URL de la vidéo", blank=True,
                               help_text="Pour YouTube ou Vimeo")
    video_file = models.FileField("Fichier vidéo", upload_to='videos/%Y/%m/', blank=True,
                                 help_text="Pour upload direct")
    thumbnail = models.ImageField("Miniature", upload_to='video_thumbnails/%Y/%m/')
    duration = models.CharField("Durée", max_length=20, blank=True, help_text="Ex: 15:30")
    
    # Organisation
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='videos'
    )
    
    # Publication
    is_active = models.BooleanField("Publié", default=True)
    is_featured = models.BooleanField("Mis en avant", default=False)
    order = models.IntegerField("Ordre", default=0)
    
    # Stats
    view_count = models.PositiveIntegerField("Vues", default=0, editable=False)
    
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)
    
    class Meta:
        verbose_name = "Ressource vidéo"
        verbose_name_plural = "Ressources vidéo"
        ordering = ['series_name', 'episode_number', 'order', '-created_at']
    
    def __str__(self):
        if self.episode_number and self.series_name:
            return f"{self.series_name} - Épisode {self.episode_number}: {self.title}"
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_embed_url(self):
        """Retourne l'URL d'embed selon le type"""
        if self.video_type == 'youtube':
            # Extraire l'ID de différents formats d'URL YouTube
            import re
            
            # Patterns pour différents formats d'URL YouTube
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
                r'youtube\.com\/embed\/([^&\n?#]+)',
                r'youtube\.com\/v\/([^&\n?#]+)',
            ]
            
            video_id = None
            for pattern in patterns:
                match = re.search(pattern, self.video_url)
                if match:
                    video_id = match.group(1)
                    break
            
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
            
        elif self.video_type == 'vimeo':
            video_id = self.video_url.split('/')[-1].split('?')[0]
            return f"https://player.vimeo.com/video/{video_id}"
        
        return None
    
    def increment_view(self):
        """Incrémente le compteur de vues"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ImageGallery(models.Model):
    """Galerie d'images pour projets et références"""
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField("Slug", unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    image = models.ImageField("Image", upload_to='gallery/%Y/%m/')
    caption = models.CharField("Légende", max_length=300, blank=True)
    
    # Organisation
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Catégorie",
        related_name='images'
    )
    
    # Publication
    is_active = models.BooleanField("Publié", default=True)
    order = models.IntegerField("Ordre", default=0)
    
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    
    class Meta:
        verbose_name = "Image de galerie"
        verbose_name_plural = "Galerie d'images"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MembershipDocument(models.Model):
    """Documents pour l'adhésion au CNIAH"""
    MEMBER_TYPE_CHOICES = [
        ('national', 'Professionnels Nationaux'),
        ('international', 'Professionnels Internationaux'),
        ('both', 'Les deux'),
    ]
    
    title = models.CharField("Titre", max_length=200)
    description = models.TextField("Description", blank=True)
    file = models.FileField("Fichier", upload_to='membership/%Y/%m/')
    file_size = models.CharField("Taille du fichier", max_length=20, blank=True,
                                help_text="Ex: 2.3 MB")
    icon = models.CharField("Icône", max_length=50, default='description',
                           help_text="Nom de l'icône Material Symbols")
    
    # Type de membre concerné
    member_type = models.CharField(
        "Type de membre",
        max_length=20,
        choices=MEMBER_TYPE_CHOICES,
        default='both'
    )
    
    # Publication
    is_active = models.BooleanField("Actif", default=True)
    order = models.IntegerField("Ordre d'affichage", default=0)
    
    # Stats
    download_count = models.PositiveIntegerField("Téléchargements", default=0, editable=False)
    
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)
    
    class Meta:
        verbose_name = "Document d'adhésion"
        verbose_name_plural = "Documents d'adhésion"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_file_extension(self):
        """Retourne l'extension du fichier"""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return 'FILE'
    
    def increment_download(self):
        """Incrémente le compteur de téléchargements"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


# ============= COTISATION =============
class CotisationDocument(models.Model):
    titre = models.CharField(max_length=200)
    fichier = models.FileField(upload_to='cotisation/')
    date_ajout = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Document de Cotisation"
        verbose_name_plural = "Documents de Cotisation"
        ordering = ['-date_ajout']
    
    def __str__(self):
        return self.titre


# ============= FORMATION CONTINUE =============
class CategoryFormation(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Catégorie de Formation"
        verbose_name_plural = "Catégories de Formation"
        ordering = ['ordre']
    
    def __str__(self):
        return self.nom


class FormationContent(models.Model):
    TYPE_CONTENU_CHOICES = [
        ('video', 'Vidéo'),
        ('image', 'Image'),
        ('pdf', 'Document PDF'),
        ('groupe_images', 'Groupe d\'images'),
    ]
    
    titre = models.CharField(max_length=200)
    date_formation = models.DateField()
    type_contenu = models.CharField(max_length=20, choices=TYPE_CONTENU_CHOICES)
    categorie = models.ForeignKey(CategoryFormation, on_delete=models.CASCADE, related_name='formations')
    video_url = models.URLField(blank=True, null=True, help_text="URL YouTube ou Vimeo")
    fichier = models.FileField(upload_to='formations/', blank=True, null=True)
    description = models.TextField()
    ordre = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Contenu de Formation"
        verbose_name_plural = "Contenus de Formation"
        ordering = ['-date_formation', 'ordre']
    
    def __str__(self):
        return f"{self.titre} ({self.date_formation})"


class FormationImage(models.Model):
    formation = models.ForeignKey(FormationContent, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='formations/images/')
    legende = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return f"Image pour {self.formation.titre}"


# ============= HONNEUR ET MERITE =============
class HonneurMerite(models.Model):
    TYPE_CONTENU_CHOICES = [
        ('video', 'Vidéo'),
        ('images', 'Images'),
        ('texte', 'Texte seulement'),
    ]
    
    annee = models.IntegerField()
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_contenu = models.CharField(max_length=20, choices=TYPE_CONTENU_CHOICES)
    video_url = models.URLField(blank=True, null=True)
    ordre = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Honneur et Mérite"
        verbose_name_plural = "Honneurs et Mérites"
        ordering = ['-annee', 'ordre']
    
    def __str__(self):
        return f"{self.annee} - {self.titre}"


class HonneurMeriteImage(models.Model):
    honneur = models.ForeignKey(HonneurMerite, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='honneur_merite/')
    legende = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return f"Image pour {self.honneur.titre}"


# ============= MEMBRES ACTIFS =============
class TitreProfessionnel(models.Model):
    nom = models.CharField(max_length=100, help_text="Ex: Ingénieur Civil, Architecte, etc.")
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Titre Professionnel"
        verbose_name_plural = "Titres Professionnels"
        ordering = ['ordre']
    
    def __str__(self):
        return self.nom


class MembreActif(models.Model):
    numero = models.CharField(max_length=20, unique=True, help_text="Numéro d'identification unique")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    titre = models.ForeignKey(TitreProfessionnel, on_delete=models.PROTECT, related_name='membres')
    photo = models.ImageField(upload_to='membres/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    date_inscription = models.DateField(default=timezone.now)
    
    class Meta:
        verbose_name = "Membre Actif"
        verbose_name_plural = "Membres Actifs"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.numero} - {self.prenom} {self.nom}"
    
    history = HistoricalRecords()

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class PageMembresActifs(models.Model):
    """Paramètres de la page Membres Actifs"""
    titre = models.CharField(max_length=200, default="Liste des Ingénieurs et Architectes Actifs")
    introduction = models.TextField(help_text="Texte d'introduction affiché en haut de la page")
    
    class Meta:
        verbose_name = "Configuration Page Membres Actifs"
        verbose_name_plural = "Configuration Page Membres Actifs"
    
    def __str__(self):
        return "Configuration Page Membres Actifs"


# ============= CERTIFICATION =============
class Certification(models.Model):
    STATUT_CHOICES = [
        ('valide', 'Valide'),
        ('expire', 'Expiré'),
        ('suspendu', 'Suspendu'),
    ]
    
    numero_certificat = models.CharField(max_length=50, unique=True)
    membre = models.ForeignKey(MembreActif, on_delete=models.CASCADE, related_name='certifications')
    date_delivrance = models.DateField()
    date_expiration = models.DateField()
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='valide')
    
    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['-date_delivrance']
    
    def __str__(self):
        return f"{self.numero_certificat} - {self.membre.nom_complet}"
    
    @property
    def est_valide(self):
        return self.statut == 'valide' and self.date_expiration >= timezone.now().date()

    def generate_qr_code(self):
        """Génère et stocke le QR code pointant vers la page de vérification."""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8002')
        qr_url = f"{site_url}/verifier-certification/?numero={self.numero_certificat}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        filename = f"qr_{self.numero_certificat}.png"
        self.qr_code.save(filename, buf, save=False)

    history = HistoricalRecords()


# ============= PLAINTES =============
class Plainte(models.Model):
    TYPE_PLAINTE_CHOICES = [
        ('ethique', 'Violation d\'éthique professionnelle'),
        ('competence', 'Compétence professionnelle'),
        ('qualite', 'Qualité des travaux'),
        ('contractuel', 'Litige contractuel'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('soumise', 'Soumise'),
        ('en_cours', 'En cours d\'examen'),
        ('traitee', 'Traitée'),
        ('classee', 'Classée'),
    ]
    
    numero_reference = models.CharField(max_length=50, unique=True, editable=False)
    nom_plaignant = models.CharField(max_length=100)
    email_plaignant = models.EmailField()
    telephone = models.CharField(max_length=20)
    membre_concerne = models.CharField(max_length=200, help_text="Nom du membre visé par la plainte")
    type_plainte = models.CharField(max_length=20, choices=TYPE_PLAINTE_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='soumise')
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    notes_internes = models.TextField(blank=True, help_text="Notes pour usage interne uniquement")
    
    class Meta:
        verbose_name = "Plainte"
        verbose_name_plural = "Plaintes"
        ordering = ['-date_soumission']
    
    def __str__(self):
        return f"{self.numero_reference} - {self.nom_plaignant}"
    
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.numero_reference:
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=4))
            self.numero_reference = f"PL-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class DocumentPlainte(models.Model):
    plainte = models.ForeignKey(Plainte, on_delete=models.CASCADE, related_name='documents')
    fichier = models.FileField(upload_to='plaintes/')
    nom_fichier = models.CharField(max_length=200)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Document de Plainte"
        verbose_name_plural = "Documents de Plainte"
    
    def __str__(self):
        return self.nom_fichier


# ============= ABOUT - DOCUMENTS HISTORIQUES =============
class DocumentHistorique(models.Model):
    nom = models.CharField(max_length=200, help_text="Ex: Décret-loi 25 Mars 1974")
    fichier = models.FileField(upload_to='historique/', validators=[FileExtensionValidator(['pdf'])])
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Document Historique"
        verbose_name_plural = "Documents Historiques"
        ordering = ['ordre']
    
    def __str__(self):
        return self.nom


# ============= COMITE DE DIRECTION =============
class ComiteDirection(models.Model):
    annee_debut = models.IntegerField()
    annee_fin = models.IntegerField()
    actif = models.BooleanField(default=False, help_text="Cocher si c'est le comité actuel")
    
    class Meta:
        verbose_name = "Comité de Direction"
        verbose_name_plural = "Comités de Direction"
        ordering = ['-annee_debut']
    
    def __str__(self):
        return f"Comité {self.annee_debut}-{self.annee_fin}"


class MembreComite(models.Model):
    POSTE_CHOICES = [
        ('president', 'Président'),
        ('vice_president', 'Vice-Président'),
        ('secretaire', 'Secrétaire Général'),
        ('tresorier', 'Trésorier'),
        ('conseiller', 'Conseiller'),
    ]
    
    comite = models.ForeignKey(ComiteDirection, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    poste = models.CharField(max_length=20, choices=POSTE_CHOICES)
    photo = models.ImageField(upload_to='comite/')
    biographie = models.TextField()
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Membre du Comité"
        verbose_name_plural = "Membres du Comité"
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.get_poste_display()}"


# ============= COMMISSION D'APUREMENT =============
class CommissionApurement(models.Model):
    annee_debut = models.IntegerField()
    annee_fin = models.IntegerField()
    actif = models.BooleanField(default=False, help_text="Cocher si c'est la commission actuelle")
    description = models.TextField(blank=True, help_text="Texte explicatif des attributions")
    
    class Meta:
        verbose_name = "Commission d'Apurement"
        verbose_name_plural = "Commissions d'Apurement"
        ordering = ['-annee_debut']
    
    def __str__(self):
        return f"Commission d'Apurement {self.annee_debut}-{self.annee_fin}"


class MembreCommission(models.Model):
    commission = models.ForeignKey(CommissionApurement, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='commission/')
    biographie = models.TextField()
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Membre de la Commission"
        verbose_name_plural = "Membres de la Commission"
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


# ============= CONSEIL DE DISCIPLINE =============
class ConseilDiscipline(models.Model):
    annee_debut = models.IntegerField()
    annee_fin = models.IntegerField()
    actif = models.BooleanField(default=False, help_text="Cocher si c'est le conseil actuel")
    
    class Meta:
        verbose_name = "Conseil de Discipline"
        verbose_name_plural = "Conseils de Discipline"
        ordering = ['-annee_debut']
    
    def __str__(self):
        return f"Conseil de Discipline {self.annee_debut}-{self.annee_fin}"


class MembreConseil(models.Model):
    conseil = models.ForeignKey(ConseilDiscipline, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='conseil/')
    biographie = models.TextField()
    ordre = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Membre du Conseil"
        verbose_name_plural = "Membres du Conseil"
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


# ============= NORMES =============
class CategoryNorme(models.Model):
    nom = models.CharField(max_length=100)
    ordre = models.IntegerField(default=0)
    icone = models.CharField(max_length=50, default='description', help_text="Nom de l'icône Material Symbols")
    
    class Meta:
        verbose_name = "Catégorie de Norme"
        verbose_name_plural = "Catégories de Normes"
        ordering = ['ordre']
    
    def __str__(self):
        return self.nom


class Norme(models.Model):
    titre = models.CharField(max_length=200)
    version = models.CharField(max_length=50)
    date_publication = models.DateField()
    categorie = models.ForeignKey(CategoryNorme, on_delete=models.PROTECT, related_name='normes')
    fichier = models.FileField(upload_to='normes/', validators=[FileExtensionValidator(['pdf'])])
    description = models.TextField()
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Norme"
        verbose_name_plural = "Normes"
        ordering = ['-date_publication']
    
    def __str__(self):
        return f"{self.titre} - {self.version}"


# ============= SPONSORS =============
class Sponsor(models.Model):
    NIVEAU_CHOICES = [
        ('platine', 'Platine'),
        ('or', 'Or'),
        ('argent', 'Argent'),
        ('bronze', 'Bronze'),
    ]
    
    nom = models.CharField(max_length=200)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    logo = models.ImageField(upload_to='sponsors/')
    description = models.TextField(blank=True)
    url_site = models.URLField(blank=True)
    ordre = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sponsor"
        verbose_name_plural = "Sponsors"
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.nom} ({self.get_niveau_display()})"

# ============= DEMANDE D'ADHÉSION =============
class DemandeAdhesion(models.Model):
    """Formulaire de demande d'admission au CNIAH (membre-01)"""

    TYPE_CHOICES = [
        ('admission', 'Nouvelle admission'),
        ('mise_a_jour', 'Mise à jour de statut'),
    ]
    STATUT_DEMANDE_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', "En cours d'examen"),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
    ]
    STATUT_MEMBRE_CHOICES = [
        ('membre', 'Membre'),
        ('postulant', 'Postulant'),
    ]

    # Méta-données de la demande
    type_demande = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='admission',
        verbose_name="Type de demande",
    )
    statut_demande = models.CharField(
        max_length=20, choices=STATUT_DEMANDE_CHOICES, default='en_attente',
        verbose_name="Statut de la demande",
    )
    statut_souhaite = models.CharField(
        max_length=20, choices=STATUT_MEMBRE_CHOICES, default='postulant',
        verbose_name="Statut souhaité",
    )

    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    titre = models.CharField(max_length=100, verbose_name="Titre professionnel")
    fonction = models.CharField(max_length=200, blank=True, verbose_name="Fonction")
    nif = models.CharField(max_length=50, blank=True, verbose_name="NIF")
    telephone = models.CharField(max_length=30, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Adresse courriel")
    adresse = models.TextField(verbose_name="Adresse")

    # Formation
    diplome_1 = models.CharField(max_length=200, verbose_name="Diplôme 1 (avec année)")
    diplome_2 = models.CharField(max_length=200, blank=True, verbose_name="Diplôme 2 (avec année)")
    cv_resume = models.TextField(blank=True, verbose_name="Curriculum Vitae (résumé)")

    # Cotisations
    don_montant = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Don (montant en HTG)",
    )

    # Pièces jointes
    photo_identite = models.ImageField(
        upload_to='adhesion/photos/', blank=True, null=True,
        verbose_name='Photo d\'identité 2"×2"',
    )
    copie_diplomes = models.FileField(
        upload_to='adhesion/diplomes/', blank=True, null=True,
        verbose_name="Copie du/des diplôme(s)",
    )
    piece_identite = models.FileField(
        upload_to='adhesion/identites/', blank=True, null=True,
        verbose_name="Pièce d'identité",
    )
    cv_fichier = models.FileField(
        upload_to='adhesion/cvs/', blank=True, null=True,
        verbose_name="CV (fichier)",
    )
    certificat_cniah = models.FileField(
        upload_to='adhesion/certificats/', blank=True, null=True,
        verbose_name="Certificat CNIAH",
    )
    lettre_support = models.FileField(
        upload_to='adhesion/lettres/', blank=True, null=True,
        verbose_name="Lettre de support",
    )
    permis_sejour = models.FileField(
        upload_to='adhesion/permis/', blank=True, null=True,
        verbose_name="Permis de séjour",
    )
    autres_documents = models.FileField(
        upload_to='adhesion/autres/', blank=True, null=True,
        verbose_name="Autres documents",
    )

    # Meta
    date_soumission = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    notes_admin = models.TextField(blank=True, verbose_name="Notes administratives")

    class Meta:
        verbose_name = "Demande d'Adhésion"
        verbose_name_plural = "Demandes d'Adhésion"
        ordering = ['-date_soumission']

    history = HistoricalRecords()

    def __str__(self):
        date_str = self.date_soumission.strftime('%d/%m/%Y') if self.date_soumission else ''
        return f"{self.prenom} {self.nom} — {self.get_type_demande_display()} ({date_str})"