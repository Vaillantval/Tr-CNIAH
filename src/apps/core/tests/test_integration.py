import pytest
from django.urls import reverse
from apps.core.models import Plainte, DocumentPlainte, Newsletter
from apps.core.tests.factories import MembreActifFactory
from apps.members.tests.factories import UserFactory, UnverifiedUserFactory


@pytest.mark.django_db
class TestFluxAdhesion:
    """Test du flux complet de demande d'adhésion."""

    def test_flux_complet(self, client):
        url = reverse('core:adhesion')
        data = {
            'type_demande': 'admission',
            'statut_souhaite': 'postulant',
            'nom': 'MARTIN',
            'prenom': 'Paul',
            'titre': 'Architecte',
            'telephone': '50987654321',
            'email': 'paul.martin@test.com',
            'adresse': '10 Rue de la Paix, Port-au-Prince',
            'diplome_1': 'Master Architecture, 2018',
        }
        response = client.post(url, data=data)
        assert response.status_code == 302

        from apps.core.models import DemandeAdhesion
        demande = DemandeAdhesion.objects.get(email='paul.martin@test.com')
        assert demande.nom == 'MARTIN'
        assert demande.statut_demande == 'en_attente'

    def test_authentifie_redirige_sans_creer(self, client):
        user = UserFactory()
        client.force_login(user)
        url = reverse('core:adhesion')
        response = client.post(url, data={'nom': 'TEST'})
        assert response.status_code == 302
        from apps.core.models import DemandeAdhesion
        assert not DemandeAdhesion.objects.exists()


@pytest.mark.django_db
class TestFluxPlainte:
    """Test de l'atomicité et du flux de dépôt de plainte."""

    def _valid_data(self, accuse_pk):
        return {
            'nom_plaignant': 'Marie Pierre',
            'email_plaignant': 'marie@test.com',
            'telephone': '50911223344',
            'membre_accuse': str(accuse_pk),
            'type_plainte': 'qualite',
            'description': 'Description très détaillée de la plainte pour validation de la longueur.',
        }

    def test_plainte_creee_avec_reference(self, client):
        accuse = MembreActifFactory()
        response = client.post(reverse('core:deposer_plainte'), data=self._valid_data(accuse.pk))
        assert response.status_code == 302
        assert Plainte.objects.count() == 1
        plainte = Plainte.objects.first()
        assert plainte.numero_reference.startswith('PL-')

    def test_plainte_lie_membre_accuse(self, client):
        accuse = MembreActifFactory()
        client.post(reverse('core:deposer_plainte'), data=self._valid_data(accuse.pk))
        plainte = Plainte.objects.first()
        assert plainte.membre_accuse == accuse

    def test_page_succes_accessible(self, client):
        accuse = MembreActifFactory()
        client.post(reverse('core:deposer_plainte'), data=self._valid_data(accuse.pk))
        plainte = Plainte.objects.first()
        response = client.get(reverse('core:plainte_success', kwargs={'numero': plainte.numero_reference}))
        assert response.status_code == 200

    def test_plainte_invalide_rien_cree(self, client):
        response = client.post(reverse('core:deposer_plainte'), data={})
        assert response.status_code == 200
        assert Plainte.objects.count() == 0


@pytest.mark.django_db
class TestFluxAuthentification:
    """Test du flux complet inscription → vérification email → connexion."""

    def test_inscription_puis_verify_puis_connexion(self, client):
        membre = MembreActifFactory()

        # Inscription
        client.post(reverse('members:inscription'), {
            'username': 'testflux',
            'email': 'testflux@test.com',
            'numero_membre': membre.numero,
            'password': 'MotDePasse123!',
            'password_confirm': 'MotDePasse123!',
        })
        from apps.members.models import User
        user = User.objects.get(username='testflux')
        assert not user.email_verified

        # Vérification email
        client.get(reverse('members:verify_email', kwargs={'token': user.email_verification_token}))
        user.refresh_from_db()
        assert user.email_verified

        # Connexion
        response = client.post(reverse('members:connexion'), {
            'username': 'testflux',
            'password': 'MotDePasse123!',
        })
        assert response.status_code == 302
        assert response.wsgi_request.user.is_authenticated

    def test_connexion_bloquee_sans_verification(self, client):
        user = UnverifiedUserFactory()
        response = client.post(reverse('members:connexion'), {
            'username': user.username,
            'password': 'testpass123!',
        })
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
class TestFluxNewsletter:
    def test_abonnement_puis_tentative_doublon(self, client):
        url = reverse('core:newsletter_subscribe')

        client.post(url, data={'email': 'unique@test.com'})
        assert Newsletter.objects.filter(email='unique@test.com').count() == 1

        # Second abonnement avec le même email
        client.post(url, data={'email': 'unique@test.com'})
        assert Newsletter.objects.filter(email='unique@test.com').count() == 1
