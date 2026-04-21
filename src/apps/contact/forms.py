from django import forms
from .models import ContactMessage, ProfessionalRequest


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 10:
            raise forms.ValidationError("Le message doit contenir au moins 10 caractères.")
        return msg

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 8:
                raise forms.ValidationError("Numéro de téléphone invalide (minimum 8 chiffres).")
        return phone


class ProfessionalRequestForm(forms.ModelForm):
    class Meta:
        model = ProfessionalRequest
        fields = ['name', 'email', 'phone', 'professional_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 20:
            raise forms.ValidationError("La description doit contenir au moins 20 caractères.")
        return desc

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 8:
                raise forms.ValidationError("Numéro de téléphone invalide (minimum 8 chiffres).")
        return phone
