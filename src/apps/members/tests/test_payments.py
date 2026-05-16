"""F9 — Tests pour PaiementCertificat et Don."""
import datetime
import pytest
from apps.members.models import PaiementCertificat, Don
from apps.members.tests.factories import UserFactory
from apps.core.tests.factories import CertificationFactory


@pytest.mark.django_db
class TestPaiementCertificat:
    def test_creation_minimale(self):
        user = UserFactory()
        paiement = PaiementCertificat.objects.create(
            user=user,
            montant=100,
            devise='usd',
        )
        assert paiement.pk is not None
        assert paiement.statut == 'en_attente'

    def test_statut_defaut_en_attente(self):
        user = UserFactory()
        p = PaiementCertificat.objects.create(user=user, montant=50, devise='htg')
        assert p.statut == 'en_attente'

    def test_annees_payees_defaut_1(self):
        user = UserFactory()
        p = PaiementCertificat.objects.create(user=user, montant=100, devise='usd')
        assert p.annees_payees == 1

    def test_lien_certification(self):
        user = UserFactory()
        cert = CertificationFactory(membre=user.membre_actif)
        p = PaiementCertificat.objects.create(
            user=user,
            certification=cert,
            montant=150,
            devise='usd',
            annees_payees=2,
        )
        assert p.certification == cert
        assert p.annees_payees == 2

    def test_str(self):
        user = UserFactory()
        p = PaiementCertificat.objects.create(user=user, montant=100, devise='usd')
        assert user.get_full_name() in str(p)

    def test_valider_paiement(self):
        user = UserFactory()
        p = PaiementCertificat.objects.create(user=user, montant=100, devise='usd')
        p.statut = 'valide'
        p.date_paiement = datetime.datetime.now()
        p.save()
        p.refresh_from_db()
        assert p.statut == 'valide'

    def test_methode_paiement_vide_par_defaut(self):
        user = UserFactory()
        p = PaiementCertificat.objects.create(user=user, montant=100, devise='usd')
        assert p.methode_paiement == ''

    def test_sans_lien_certification(self):
        user = UserFactory()
        p = PaiementCertificat.objects.create(user=user, montant=100, devise='usd')
        assert p.certification is None


@pytest.mark.django_db
class TestDon:
    def test_creation_anonyme(self):
        don = Don.objects.create(
            nom_donateur='Anonyme',
            email_donateur='anon@test.com',
            montant=500,
            devise='htg',
        )
        assert don.pk is not None
        assert don.user is None
        assert don.statut == 'recu'

    def test_creation_membre(self):
        user = UserFactory()
        don = Don.objects.create(user=user, montant=1000, devise='htg')
        assert don.user == user

    def test_statut_defaut_recu(self):
        don = Don.objects.create(montant=100, devise='usd')
        assert don.statut == 'recu'

    def test_devise_defaut_htg(self):
        don = Don.objects.create(montant=100)
        assert don.devise == 'htg'

    def test_message_optionnel(self):
        don = Don.objects.create(montant=200, devise='htg', message='Bonne chance !')
        assert don.message == 'Bonne chance !'

    def test_confirmer_don(self):
        don = Don.objects.create(montant=100, devise='htg')
        don.statut = 'confirme'
        don.save()
        don.refresh_from_db()
        assert don.statut == 'confirme'

    def test_nom_donateur_optionnel(self):
        user = UserFactory()
        don = Don.objects.create(user=user, montant=100, devise='htg')
        assert don.nom_donateur == ''
