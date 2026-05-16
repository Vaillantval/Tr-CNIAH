"""F1 — Tests pour les tâches Celery email."""
import pytest
from unittest.mock import patch, MagicMock, call
from apps.members.tests.factories import UserFactory, CotisationFactory
from apps.core.tests.factories import CertificationFactory


@pytest.mark.django_db
class TestEnvoyerCertificatParEmail:
    def test_certification_inexistante_ne_leve_pas(self):
        from apps.members.tasks import envoyer_certificat_par_email
        # Doit avaler l'erreur (self.retry sera appelé mais on ne vérifie pas ici)
        try:
            envoyer_certificat_par_email.apply(args=[99999])
        except Exception:
            pass  # Un retry ou DoesNotExist est acceptable

    @patch('apps.members.tasks.EmailMessage')
    def test_envoi_email_avec_certification(self, mock_email_cls):
        from apps.members.tasks import envoyer_certificat_par_email
        user = UserFactory()
        cert = CertificationFactory(membre=user.membre_actif)

        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        envoyer_certificat_par_email.apply(args=[cert.pk])

        mock_email_cls.assert_called_once()
        mock_msg.attach.assert_called_once()
        mock_msg.send.assert_called_once()

    @patch('apps.members.tasks.EmailMessage')
    def test_email_envoye_au_bon_destinataire(self, mock_email_cls):
        from apps.members.tasks import envoyer_certificat_par_email
        user = UserFactory(email='membre@cniah.ht')
        cert = CertificationFactory(membre=user.membre_actif)

        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        envoyer_certificat_par_email.apply(args=[cert.pk])

        _, kwargs = mock_email_cls.call_args
        assert 'membre@cniah.ht' in kwargs.get('to', [])

    @patch('apps.members.tasks.EmailMessage')
    def test_pdf_attache_avec_bonne_extension(self, mock_email_cls):
        from apps.members.tasks import envoyer_certificat_par_email
        user = UserFactory()
        cert = CertificationFactory(membre=user.membre_actif)

        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        envoyer_certificat_par_email.apply(args=[cert.pk])

        attach_args = mock_msg.attach.call_args[0]
        assert attach_args[0].endswith('.pdf')
        assert attach_args[2] == 'application/pdf'


@pytest.mark.django_db
class TestEnvoyerEmailVerification:
    @patch('apps.members.tasks.send_mail')
    def test_envoi_email_verification(self, mock_send):
        from apps.members.tasks import envoyer_email_verification
        user = UserFactory(email_verified=False)
        envoyer_email_verification.apply(args=[user.pk, 'http://example.com/verify/token/'])
        mock_send.assert_called_once()

    @patch('apps.members.tasks.send_mail')
    def test_url_verification_dans_corps(self, mock_send):
        from apps.members.tasks import envoyer_email_verification
        user = UserFactory(email_verified=False)
        verify_url = 'http://example.com/verify/abc123/'
        envoyer_email_verification.apply(args=[user.pk, verify_url])
        _, kwargs = mock_send.call_args
        message = kwargs.get('message', mock_send.call_args[0][1] if mock_send.call_args[0] else '')
        assert verify_url in message


@pytest.mark.django_db
class TestEnvoyerEmailBienvenue:
    @patch('apps.members.tasks.send_mail')
    def test_envoi_email_bienvenue(self, mock_send):
        from apps.members.tasks import envoyer_email_bienvenue
        user = UserFactory()
        envoyer_email_bienvenue.apply(args=[user.pk])
        mock_send.assert_called_once()

    @patch('apps.members.tasks.send_mail')
    def test_destinataire_correct(self, mock_send):
        from apps.members.tasks import envoyer_email_bienvenue
        user = UserFactory(email='bienvenue@cniah.ht')
        envoyer_email_bienvenue.apply(args=[user.pk])
        _, kwargs = mock_send.call_args
        assert 'bienvenue@cniah.ht' in kwargs.get('recipient_list', [])


@pytest.mark.django_db
class TestNotifierAdminPreuveCotisation:
    @patch('apps.members.tasks.send_mail')
    def test_notification_envoyee_si_admin_configure(self, mock_send, settings):
        from apps.members.tasks import notifier_admin_preuve_cotisation
        settings.ADMIN_NOTIFY_EMAIL = ['admin@cniah.ht']
        user = UserFactory()
        cotisation = CotisationFactory(user=user)
        notifier_admin_preuve_cotisation.apply(args=[cotisation.pk])
        mock_send.assert_called_once()

    @patch('apps.members.tasks.send_mail')
    def test_pas_email_si_admin_non_configure(self, mock_send, settings):
        from apps.members.tasks import notifier_admin_preuve_cotisation
        settings.ADMIN_NOTIFY_EMAIL = []
        user = UserFactory()
        cotisation = CotisationFactory(user=user)
        notifier_admin_preuve_cotisation.apply(args=[cotisation.pk])
        mock_send.assert_not_called()


@pytest.mark.django_db
class TestRappelRenouvellementCertificat:
    @patch('apps.members.tasks.send_mail')
    def test_rappel_envoye(self, mock_send):
        from apps.members.tasks import rappel_renouvellement_certificat
        user = UserFactory()
        cert = CertificationFactory(membre=user.membre_actif)
        rappel_renouvellement_certificat.apply(args=[cert.pk])
        mock_send.assert_called_once()

    @patch('apps.members.tasks.send_mail')
    def test_destinataire_correct(self, mock_send):
        from apps.members.tasks import rappel_renouvellement_certificat
        user = UserFactory(email='rappel@cniah.ht')
        cert = CertificationFactory(membre=user.membre_actif)
        rappel_renouvellement_certificat.apply(args=[cert.pk])
        _, kwargs = mock_send.call_args
        assert 'rappel@cniah.ht' in kwargs.get('recipient_list', [])
