import pytest
from django.urls import reverse
from apps.members.tests.factories import UserFactory, CotisationFactory


@pytest.mark.django_db
class TestDashboard:
    def test_anonyme_redirige(self, client):
        response = client.get(reverse('members:dashboard'))
        assert response.status_code == 302
        assert '/connexion/' in response['Location']

    def test_membre_acces(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse('members:dashboard'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestProfil:
    def test_anonyme_redirige(self, client):
        response = client.get(reverse('members:mon_profil'))
        assert response.status_code == 302

    def test_get(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse('members:mon_profil'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_mise_a_jour_telephone(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.post(reverse('members:mon_profil'), {'phone': '50998765432'})
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.phone == '50998765432'

    def test_telephone_invalide(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.post(reverse('members:mon_profil'), {'phone': '123'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestCotisations:
    def test_anonyme_redirige(self, client):
        response = client.get(reverse('members:mes_cotisations'))
        assert response.status_code == 302

    def test_liste_affichee(self, client):
        user = UserFactory()
        CotisationFactory(user=user)
        client.force_login(user)
        response = client.get(reverse('members:mes_cotisations'))
        assert response.status_code == 200
        assert len(response.context['cotisations']) == 1

    def test_acces_cotisation_autre_utilisateur_interdit(self, client):
        user_a = UserFactory()
        user_b = UserFactory()
        cotisation_b = CotisationFactory(user=user_b)
        client.force_login(user_a)
        # user_a tente de soumettre une preuve pour la cotisation de user_b
        from django.core.files.uploadedfile import SimpleUploadedFile
        preuve = SimpleUploadedFile("preuve.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        response = client.post(reverse('members:mes_cotisations'), {
            'cotisation_id': cotisation_b.id,
            'preuve_paiement': preuve,
        })
        # Doit retourner 404 car la cotisation n'appartient pas à user_a
        assert response.status_code == 404


@pytest.mark.django_db
class TestDocuments:
    def test_anonyme_redirige(self, client):
        response = client.get(reverse('members:documents'))
        assert response.status_code == 302

    def test_membre_acces(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse('members:documents'))
        assert response.status_code == 200
