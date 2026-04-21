import pytest
from django.urls import reverse
from apps.members.models import ForumReponse
from apps.members.tests.factories import UserFactory, ForumCategorieFactory, ForumSujetFactory


@pytest.mark.django_db
class TestForum:
    def test_anonyme_redirige(self, client):
        response = client.get(reverse('members:forum'))
        assert response.status_code == 302

    def test_membre_acces(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse('members:forum'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestNouveauSujet:
    def test_anonyme_redirige(self, client):
        cat = ForumCategorieFactory()
        response = client.get(reverse('members:nouveau_sujet', kwargs={'categorie_id': cat.id}))
        assert response.status_code == 302

    def test_creation_valide(self, client):
        user = UserFactory()
        cat = ForumCategorieFactory()
        client.force_login(user)
        response = client.post(
            reverse('members:nouveau_sujet', kwargs={'categorie_id': cat.id}),
            {'categorie': cat.id, 'titre': 'Mon sujet de test', 'contenu': 'Contenu du sujet de test.'},
        )
        assert response.status_code == 302
        assert cat.sujets.filter(auteur=user).exists()

    def test_titre_trop_court(self, client):
        user = UserFactory()
        cat = ForumCategorieFactory()
        client.force_login(user)
        response = client.post(
            reverse('members:nouveau_sujet', kwargs={'categorie_id': cat.id}),
            {'categorie': cat.id, 'titre': 'Abc', 'contenu': 'Contenu valide.'},
        )
        assert response.status_code == 200
        assert not cat.sujets.exists()


@pytest.mark.django_db
class TestReponseForumSujet:
    def test_anonyme_redirige(self, client):
        sujet = ForumSujetFactory()
        response = client.get(reverse('members:forum_sujet', kwargs={'sujet_id': sujet.id}))
        assert response.status_code == 302

    def test_reponse_valide(self, client):
        user = UserFactory()
        sujet = ForumSujetFactory()
        client.force_login(user)
        response = client.post(
            reverse('members:forum_sujet', kwargs={'sujet_id': sujet.id}),
            {'contenu': 'Ma réponse au sujet de test.'},
        )
        assert response.status_code == 302
        assert ForumReponse.objects.filter(sujet=sujet, auteur=user).exists()

    def test_reponse_trop_courte(self, client):
        user = UserFactory()
        sujet = ForumSujetFactory()
        client.force_login(user)
        response = client.post(
            reverse('members:forum_sujet', kwargs={'sujet_id': sujet.id}),
            {'contenu': 'Mm'},
        )
        assert response.status_code == 200
        assert not ForumReponse.objects.filter(sujet=sujet).exists()
