"""F5 — Tests pour le certificat PDF et la vue mon_certificat."""
import datetime
import pytest
from django.urls import reverse
from apps.core.tests.factories import CertificationFactory, MembreActifFactory
from apps.members.tests.factories import UserFactory


@pytest.mark.django_db
class TestMonCertificatView:
    def test_anonyme_redirige_connexion(self, client):
        url = reverse('members:mon_certificat')
        response = client.get(url)
        assert response.status_code == 302
        assert 'connexion' in response['Location']

    def test_affiche_certificat(self, client):
        user = UserFactory()
        cert = CertificationFactory(membre=user.membre_actif)
        client.force_login(user)
        url = reverse('members:mon_certificat')
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['certification'] == cert

    def test_sans_certification_redirige_dashboard(self, client):
        user = UserFactory()
        client.force_login(user)
        url = reverse('members:mon_certificat')
        response = client.get(url)
        assert response.status_code == 302
        assert 'dashboard' in response['Location']

    def test_download_pdf_retourne_bytes(self, client):
        user = UserFactory()
        CertificationFactory(membre=user.membre_actif)
        client.force_login(user)
        url = reverse('members:mon_certificat') + '?download=1'
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert response['Content-Disposition'].startswith('attachment')

    def test_download_pdf_contenu_non_vide(self, client):
        user = UserFactory()
        CertificationFactory(membre=user.membre_actif)
        client.force_login(user)
        url = reverse('members:mon_certificat') + '?download=1'
        response = client.get(url)
        assert len(response.content) > 1000  # PDF minimum viable

    def test_send_email_redirige(self, client, settings):
        settings.CELERY_TASK_ALWAYS_EAGER = True
        user = UserFactory()
        CertificationFactory(membre=user.membre_actif)
        client.force_login(user)
        url = reverse('members:mon_certificat') + '?send_email=1'
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestGenerationPDF:
    """Teste directement la fonction utilitaire generer_certificat_pdf."""

    def test_retourne_bytes(self):
        from apps.core.utils import generer_certificat_pdf
        cert = CertificationFactory(
            date_delivrance=datetime.date(2025, 1, 1),
            annees_validite=1,
        )
        result = generer_certificat_pdf(cert)
        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'

    def test_pdf_non_vide(self):
        from apps.core.utils import generer_certificat_pdf
        cert = CertificationFactory()
        result = generer_certificat_pdf(cert)
        assert len(result) > 500

    def test_nom_membre_dans_pdf(self):
        from apps.core.utils import generer_certificat_pdf
        membre = MembreActifFactory(nom='TESTNOMCERT', prenom='PrenomTest')
        cert = CertificationFactory(membre=membre)
        pdf_bytes = generer_certificat_pdf(cert)
        # Le PDF contient le nom en majuscules dans le flux
        assert b'TESTNOMCERT' in pdf_bytes
