import pytest
from django.urls import reverse
from apps.members.models import User
from apps.members.tests.factories import UserFactory, UnverifiedUserFactory
from apps.core.tests.factories import MembreActifFactory


@pytest.mark.django_db
class TestInscription:
    def test_get(self, client):
        response = client.get(reverse('members:inscription'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_succes(self, client):
        membre = MembreActifFactory()
        data = {
            'username': 'nouveau_user',
            'email': 'nouveau@test.com',
            'numero_membre': membre.numero,
            'password': 'MotDePasse123!',
            'password_confirm': 'MotDePasse123!',
        }
        response = client.post(reverse('members:inscription'), data=data)
        assert response.status_code == 302
        assert User.objects.filter(username='nouveau_user').exists()

    def test_mot_de_passe_mismatch(self, client):
        membre = MembreActifFactory()
        data = {
            'username': 'user2',
            'email': 'user2@test.com',
            'numero_membre': membre.numero,
            'password': 'MotDePasse123!',
            'password_confirm': 'AutreMotDePasse!',
        }
        response = client.post(reverse('members:inscription'), data=data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert not User.objects.filter(username='user2').exists()

    def test_username_deja_pris(self, client):
        existing = UserFactory()
        membre = MembreActifFactory()
        data = {
            'username': existing.username,
            'email': 'autre@test.com',
            'numero_membre': membre.numero,
            'password': 'MotDePasse123!',
            'password_confirm': 'MotDePasse123!',
        }
        response = client.post(reverse('members:inscription'), data=data)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_numero_membre_invalide(self, client):
        data = {
            'username': 'user3',
            'email': 'user3@test.com',
            'numero_membre': 'INVALIDE-9999',
            'password': 'MotDePasse123!',
            'password_confirm': 'MotDePasse123!',
        }
        response = client.post(reverse('members:inscription'), data=data)
        assert response.status_code == 200
        assert not User.objects.filter(username='user3').exists()


@pytest.mark.django_db
class TestConnexion:
    def test_get(self, client):
        response = client.get(reverse('members:connexion'))
        assert response.status_code == 200

    def test_connexion_valide(self, client):
        user = UserFactory()
        response = client.post(reverse('members:connexion'), {
            'username': user.username,
            'password': 'testpass123!',
        })
        assert response.status_code == 302

    def test_connexion_email_non_verifie(self, client):
        user = UnverifiedUserFactory()
        response = client.post(reverse('members:connexion'), {
            'username': user.username,
            'password': 'testpass123!',
        })
        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated

    def test_identifiants_incorrects(self, client):
        response = client.post(reverse('members:connexion'), {
            'username': 'inexistant',
            'password': 'mauvais',
        })
        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated

    def test_authentifie_redirige(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse('members:connexion'))
        assert response.status_code == 302


@pytest.mark.django_db
class TestVerifyEmail:
    def test_token_valide(self, client):
        user = UnverifiedUserFactory()
        token = user.email_verification_token
        response = client.get(reverse('members:verify_email', kwargs={'token': token}))
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.email_verified is True
        assert user.email_verification_token == ''

    def test_token_invalide(self, client):
        response = client.get(reverse('members:verify_email', kwargs={'token': 'token-invalide'}))
        assert response.status_code == 302
        # Vérifie le message d'erreur
        messages = list(response.wsgi_request._messages)
        assert any('invalide' in str(m).lower() for m in messages)


@pytest.mark.django_db
class TestDeconnexion:
    def test_deconnexion(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse('members:deconnexion'))
        assert response.status_code == 302
        assert not response.wsgi_request.user.is_authenticated

    def test_anonyme_redirige(self, client):
        response = client.get(reverse('members:deconnexion'))
        assert response.status_code == 302
