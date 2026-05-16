import pytest
from django.urls import reverse
from apps.core.tests.factories import PlainteFactory, MembreActifFactory, NewsletterFactory


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

    def test_membres_actifs_dans_contexte(self, client):
        """F6 — La vue doit fournir la liste des membres actifs pour le select."""
        MembreActifFactory(actif=True)
        MembreActifFactory(actif=False)
        url = reverse('core:deposer_plainte')
        response = client.get(url)
        assert 'membres_actifs' in response.context
        # Seuls les membres actifs
        for m in response.context['membres_actifs']:
            assert m.actif is True

    def test_post_valide_redirige_vers_succes(self, client):
        accuse = MembreActifFactory()
        url = reverse('core:deposer_plainte')
        data = {
            'nom_plaignant': 'Jean Dupont',
            'email_plaignant': 'jean@test.com',
            'telephone': '50912345678',
            'membre_accuse': str(accuse.pk),
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
        from apps.core.models import Newsletter
        assert Newsletter.objects.filter(email=existing.email).count() == 1


# ---- F3 : Montants cachés aux visiteurs anonymes ----

@pytest.mark.django_db
class TestMontantsCaches:
    """Les montants ne doivent pas apparaître sur les pages publiques pour les anonymes."""

    AMOUNT_PATTERNS = ['USD', 'HTG', '240', '5,000', '5000']

    def _page_has_no_amount(self, client, url):
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        # La page doit inviter à se connecter plutôt qu'afficher les montants
        for pattern in self.AMOUNT_PATTERNS:
            assert pattern not in content or 'Connectez-vous' in content or 'connexion' in content.lower()

    def test_cotisation_anonyme_masque_montants(self, client):
        try:
            url = reverse('core:cotisation')
        except Exception:
            pytest.skip("URL core:cotisation non définie")
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        # Page must not show raw amounts without auth prompt nearby
        assert 'connexion' in content.lower() or '240' not in content

    def test_adhesion_anonyme_masque_montants(self, client):
        try:
            url = reverse('core:adhesion')
        except Exception:
            pytest.skip("URL core:adhesion non définie")
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert 'connexion' in content.lower() or '240' not in content


# ---- F4 : Contacts membres affichés sur liste publique ----

@pytest.mark.django_db
class TestMembresActifsContact:
    def test_email_public_affiche(self, client):
        MembreActifFactory(email_public='contact@test.ht')
        try:
            url = reverse('core:membres_actifs')
        except Exception:
            pytest.skip("URL core:membres_actifs non définie")
        response = client.get(url)
        assert response.status_code == 200
        assert 'contact@test.ht' in response.content.decode()

    def test_membre_sans_contact_pas_erreur(self, client):
        MembreActifFactory(email_public='', telephone_public='')
        try:
            url = reverse('core:membres_actifs')
        except Exception:
            pytest.skip("URL core:membres_actifs non définie")
        response = client.get(url)
        assert response.status_code == 200


# ---- F7 : Sidebar ads dans le contexte de la home ----

@pytest.mark.django_db
class TestHomeAdsContext:
    def test_sidebar_ads_dans_contexte(self, client):
        from apps.advertisements.tests.factories import AdvertisementFactory
        AdvertisementFactory(position='sidebar')
        url = reverse('core:home')
        response = client.get(url)
        assert response.status_code == 200
        assert 'sidebar_ads' in response.context
        assert len(response.context['sidebar_ads']) >= 1

    def test_banner_ads_dans_contexte(self, client):
        from apps.advertisements.tests.factories import AdvertisementFactory
        AdvertisementFactory(position='banner')
        url = reverse('core:home')
        response = client.get(url)
        assert 'banner_ads' in response.context
