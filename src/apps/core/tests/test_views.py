import pytest
from django.urls import reverse
from apps.core.tests.factories import PlainteFactory, MembreActifFactory


@pytest.mark.django_db
class TestHomeView:
    def test_status_200(self, client):
        url = reverse('core:home')
        response = client.get(url)
        assert response.status_code == 200

    def test_template(self, client):
        url = reverse('core:home')
        response = client.get(url)
        assert 'pages/home.html' in [t.name for t in response.templates]


@pytest.mark.django_db
class TestAdhesionView:
    def test_get_anonyme(self, client):
        url = reverse('core:adhesion')
        response = client.get(url)
        assert response.status_code == 200

    def test_get_authentifie_redirige(self, client, django_user_model):
        from apps.members.tests.factories import UserFactory
        user = UserFactory()
        client.force_login(user)
        url = reverse('core:adhesion')
        response = client.get(url)
        assert response.status_code == 302

    def test_post_invalide_reste_sur_page(self, client):
        url = reverse('core:adhesion')
        response = client.post(url, data={})
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_valide_redirige(self, client):
        url = reverse('core:adhesion')
        data = {
            'type_demande': 'admission',
            'statut_souhaite': 'postulant',
            'nom': 'DUPONT',
            'prenom': 'Jean',
            'titre': 'Ingénieur Civil',
            'telephone': '50912345678',
            'email': 'jean@test.com',
            'adresse': '14 Rue Capois',
            'diplome_1': 'Licence GC 2015',
        }
        response = client.post(url, data=data)
        assert response.status_code == 302


@pytest.mark.django_db
class TestDeposerPlainte:
    def test_get(self, client):
        url = reverse('core:deposer_plainte')
        response = client.get(url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_invalide(self, client):
        url = reverse('core:deposer_plainte')
        response = client.post(url, data={})
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_valide_redirige_vers_succes(self, client):
        url = reverse('core:deposer_plainte')
        data = {
            'nom_plaignant': 'Jean Dupont',
            'email_plaignant': 'jean@test.com',
            'telephone': '50912345678',
            'membre_concerne': 'Pierre Martin',
            'type_plainte': 'ethique',
            'description': 'Description suffisamment longue pour passer la validation du formulaire.',
        }
        response = client.post(url, data=data)
        assert response.status_code == 302
        assert '/plainte-success/' in response['Location']


@pytest.mark.django_db
class TestMembersDashboardView:
    def test_anonyme_redirige_vers_login(self, client):
        url = reverse('core:members_dashboard')
        response = client.get(url)
        assert response.status_code == 302
        assert '/connexion/' in response['Location']

    def test_membre_redirige_vers_dashboard(self, client):
        from apps.members.tests.factories import UserFactory
        user = UserFactory()
        client.force_login(user)
        url = reverse('core:members_dashboard')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestNewsletter:
    def test_email_valide_redirige(self, client):
        url = reverse('core:newsletter_subscribe')
        response = client.post(url, data={'email': 'nouveau@test.com'})
        assert response.status_code == 302

    def test_email_double_affiche_erreur(self, client):
        from apps.core.tests.factories import NewsletterFactory
        existing = NewsletterFactory()
        url = reverse('core:newsletter_subscribe')
        client.post(url, data={'email': existing.email})
        # Vérifie que le doublon n'est pas créé
        from apps.core.models import Newsletter
        assert Newsletter.objects.filter(email=existing.email).count() == 1
