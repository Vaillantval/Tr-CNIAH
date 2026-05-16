from django import forms
from .models import DemandeAdhesion, Plainte, Newsletter, MembreActif
from .validators import (
    FileExtensionValidator, FileSizeValidator,
    ALLOWED_FILE_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS,
)


class MultipleFileInput(forms.FileInput):
    """FileInput qui accepte la sélection de plusieurs fichiers (Django 4.2+)."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """FileField qui accepte et valide plusieurs fichiers."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        return single_clean(data, initial)

_image_validators = [
    FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
    FileSizeValidator(),
]
_doc_validators = [
    FileExtensionValidator(ALLOWED_DOCUMENT_EXTENSIONS),
    FileSizeValidator(),
]
_any_validators = [
    FileExtensionValidator(ALLOWED_FILE_EXTENSIONS),
    FileSizeValidator(),
]


class AdhesionForm(forms.ModelForm):
    photo_identite = forms.ImageField(
        required=False,
        validators=_image_validators,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'}),
    )
    copie_diplomes = forms.FileField(
        required=False,
        validators=_any_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
    )
    piece_identite = forms.FileField(
        required=False,
        validators=_any_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
    )
    cv_fichier = forms.FileField(
        required=False,
        validators=_doc_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
    )
    certificat_cniah = forms.FileField(
        required=False,
        validators=_doc_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
    )
    lettre_support = forms.FileField(
        required=False,
        validators=_doc_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
    )
    permis_sejour = forms.FileField(
        required=False,
        validators=_any_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
    )
    autres_documents = forms.FileField(
        required=False,
        validators=_any_validators,
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
    )

    class Meta:
        model = DemandeAdhesion
        fields = [
            'type_demande', 'statut_souhaite',
            'nom', 'prenom', 'titre', 'fonction', 'nif',
            'telephone', 'email', 'adresse',
            'diplome_1', 'diplome_2', 'cv_resume',
            'don_montant',
            'photo_identite', 'copie_diplomes', 'piece_identite',
            'cv_fichier', 'certificat_cniah', 'lettre_support',
            'permis_sejour', 'autres_documents',
        ]

    def clean_telephone(self):
        tel = self.cleaned_data.get('telephone', '').strip()
        digits = ''.join(c for c in tel if c.isdigit())
        if len(digits) < 8:
            raise forms.ValidationError("Numéro de téléphone invalide (minimum 8 chiffres).")
        return tel

    def clean_don_montant(self):
        montant = self.cleaned_data.get('don_montant')
        if montant is not None and montant < 0:
            raise forms.ValidationError("Le montant du don ne peut pas être négatif.")
        return montant

    def clean_nom(self):
        return self.cleaned_data.get('nom', '').strip().upper()

    def clean_prenom(self):
        return self.cleaned_data.get('prenom', '').strip().capitalize()


class PlainteForm(forms.ModelForm):
    membre_accuse = forms.ModelChoiceField(
        queryset=MembreActif.objects.filter(actif=True).order_by('nom', 'prenom'),
        label="Membre accusé",
        help_text="Sélectionnez le membre actif du CNIAH visé par cette plainte.",
        empty_label="— Sélectionner un membre —",
        widget=forms.Select(attrs={'class': 'select2-membre'}),
    )
    documents = MultipleFileField(
        required=False,
        validators=_any_validators,
        label="Pièces jointes",
        help_text="Formats acceptés : PDF, Word, JPG, PNG. Taille max : 5 Mo par fichier.",
    )

    class Meta:
        model = Plainte
        fields = [
            'nom_plaignant', 'email_plaignant', 'telephone',
            'membre_accuse', 'type_plainte', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_telephone(self):
        tel = self.cleaned_data.get('telephone', '').strip()
        digits = ''.join(c for c in tel if c.isdigit())
        if len(digits) < 8:
            raise forms.ValidationError("Numéro de téléphone invalide (minimum 8 chiffres).")
        return tel

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 20:
            raise forms.ValidationError("La description doit contenir au moins 20 caractères.")
        return desc


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Newsletter.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse est déjà inscrite à la newsletter.")
        return email
