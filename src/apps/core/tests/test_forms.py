import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.core.forms import PlainteForm, NewsletterForm, AdhesionForm
from apps.core.tests.factories import NewsletterFactory, MembreActifFactory


# ---- PlainteForm ----

@pytest.mark.django_db
class TestPlainteForm:
    def _valid_data(self, accuse_pk):
        return {
            'nom_plaignant': 'Jean Dupont',
            'email_plaignant': 'jean@test.com',
            'telephone': '50912345678',
            'membre_accuse': str(accuse_pk),
            'type_plainte': 'ethique',
            'description': 'Description suffisamment longue pour passer la validation.',
        }

    def test_form_valide(self):
        accuse = MembreActifFactory()
        form = PlainteForm(data=self._valid_data(accuse.pk))
        assert form.is_valid(), form.errors

    def test_membre_accuse_requis(self):
        data = self._valid_data(1)
        data['membre_accuse'] = ''
        form = PlainteForm(data=data)
        assert not form.is_valid()
        assert 'membre_accuse' in form.errors

    def test_membre_accuse_inactif_invalide(self):
        inactif = MembreActifFactory(actif=False)
        form = PlainteForm(data=self._valid_data(inactif.pk))
        assert not form.is_valid()
        assert 'membre_accuse' in form.errors

    def test_telephone_trop_court(self):
        accuse = MembreActifFactory()
        data = self._valid_data(accuse.pk)
        data['telephone'] = '123'
        form = PlainteForm(data=data)
        assert not form.is_valid()
        assert 'telephone' in form.errors

    def test_description_trop_courte(self):
        accuse = MembreActifFactory()
        data = self._valid_data(accuse.pk)
        data['description'] = 'Court.'
        form = PlainteForm(data=data)
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_email_invalide(self):
        accuse = MembreActifFactory()
        data = self._valid_data(accuse.pk)
        data['email_plaignant'] = 'pas-un-email'
        form = PlainteForm(data=data)
        assert not form.is_valid()
        assert 'email_plaignant' in form.errors

    def test_fichier_extension_invalide(self):
        accuse = MembreActifFactory()
        fichier = SimpleUploadedFile("malware.exe", b"contenu", content_type="application/octet-stream")
        form = PlainteForm(data=self._valid_data(accuse.pk), files={'documents': fichier})
        assert not form.is_valid()
        assert 'documents' in form.errors

    def test_fichier_trop_volumineux(self):
        accuse = MembreActifFactory()
        gros_fichier = SimpleUploadedFile("gros.pdf", b"x" * (6 * 1024 * 1024), content_type="application/pdf")
        form = PlainteForm(data=self._valid_data(accuse.pk), files={'documents': gros_fichier})
        assert not form.is_valid()
        assert 'documents' in form.errors


# ---- NewsletterForm ----

@pytest.mark.django_db
class TestNewsletterForm:
    def test_email_valide(self):
        form = NewsletterForm(data={'email': 'nouveau@test.com'})
        assert form.is_valid(), form.errors

    def test_email_en_double(self):
        existing = NewsletterFactory()
        form = NewsletterForm(data={'email': existing.email})
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_email_invalide(self):
        form = NewsletterForm(data={'email': 'pas-un-email'})
        assert not form.is_valid()


# ---- AdhesionForm ----

class TestAdhesionForm:
    def _valid_data(self):
        return {
            'type_demande': 'admission',
            'statut_souhaite': 'postulant',
            'nom': 'DUPONT',
            'prenom': 'Jean',
            'titre': 'Ingénieur Civil',
            'telephone': '50912345678',
            'email': 'jean@test.com',
            'adresse': '14 Rue Capois, Port-au-Prince',
            'diplome_1': 'Licence en Génie Civil, 2015',
        }

    def test_form_valide(self):
        form = AdhesionForm(data=self._valid_data())
        assert form.is_valid(), form.errors

    def test_telephone_invalide(self):
        data = self._valid_data()
        data['telephone'] = '123'
        form = AdhesionForm(data=data)
        assert not form.is_valid()
        assert 'telephone' in form.errors

    def test_don_negatif(self):
        data = self._valid_data()
        data['don_montant'] = '-100'
        form = AdhesionForm(data=data)
        assert not form.is_valid()
        assert 'don_montant' in form.errors

    def test_nom_majuscule(self):
        data = self._valid_data()
        data['nom'] = 'dupont'
        form = AdhesionForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data['nom'] == 'DUPONT'
