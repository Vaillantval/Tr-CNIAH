from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from apps.core.validators import FileExtensionValidator, FileSizeValidator, ALLOWED_FILE_EXTENSIONS
from .models import User, ForumSujet, ForumReponse

_proof_validators = [
    FileExtensionValidator(ALLOWED_FILE_EXTENSIONS),
    FileSizeValidator(),
]


class InscriptionForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    numero_membre = forms.CharField(
        max_length=50,
        label="Numéro de membre CNIAH",
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('password_confirm')
        if password and confirm and password != confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
        return cleaned


class ConnexionForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


class ProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone']
        labels = {'phone': 'Téléphone'}

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 8:
                raise ValidationError("Numéro de téléphone invalide (minimum 8 chiffres).")
        return phone


class CotisationProofForm(forms.Form):
    cotisation_id = forms.IntegerField(widget=forms.HiddenInput)
    reference = forms.CharField(
        max_length=100,
        required=False,
        label="Référence de paiement",
    )
    preuve_paiement = forms.FileField(
        label="Preuve de paiement",
        validators=_proof_validators,
        widget=forms.ClearableFileInput(attrs={
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
        }),
    )


class NouveauSujetForm(forms.ModelForm):
    class Meta:
        model = ForumSujet
        fields = ['categorie', 'titre', 'contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_titre(self):
        titre = self.cleaned_data.get('titre', '').strip()
        if len(titre) < 5:
            raise ValidationError("Le titre doit contenir au moins 5 caractères.")
        return titre

    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu', '').strip()
        if len(contenu) < 10:
            raise ValidationError("Le contenu doit contenir au moins 10 caractères.")
        return contenu


class ReponseForumForm(forms.ModelForm):
    class Meta:
        model = ForumReponse
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {'contenu': 'Votre réponse'}

    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu', '').strip()
        if len(contenu) < 5:
            raise ValidationError("La réponse doit contenir au moins 5 caractères.")
        return contenu
