import pytest
from django.urls import reverse
from apps.contact.models import ContactMessage, ProfessionalRequest


@pytest.mark.django_db
class TestContactView:
    def _valid_data(self):
        return {
            'name': 'Jean Dupont',
            'email': 'jean@test.com',
            'subject': 'general',
            'message': 'Message de test suffisamment long.',
        }

    def test_get(self, client):
        response = client.get(reverse('contact:contact'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_valide_sauvegarde(self, client):
        response = client.post(reverse('contact:contact'), data=self._valid_data())
        assert response.status_code == 302
        assert ContactMessage.objects.filter(email='jean@test.com').exists()

    def test_post_message_trop_court(self, client):
        data = self._valid_data()
        data['message'] = 'Court'
        response = client.post(reverse('contact:contact'), data=data)
        assert response.status_code == 200
        assert not ContactMessage.objects.exists()

    def test_post_email_invalide(self, client):
        data = self._valid_data()
        data['email'] = 'pas-un-email'
        response = client.post(reverse('contact:contact'), data=data)
        assert response.status_code == 200
        assert not ContactMessage.objects.exists()

    def test_champs_requis_manquants(self, client):
        response = client.post(reverse('contact:contact'), data={})
        assert response.status_code == 200
        assert not ContactMessage.objects.exists()
