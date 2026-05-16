import datetime
import pytest
from apps.core.models import Plainte, Newsletter, MembreActif, Certification, ConfigurationCertificat
from apps.core.tests.factories import PlainteFactory, NewsletterFactory, MembreActifFactory


@pytest.mark.django_db
class TestPlainte:
    def test_numero_reference_auto_genere(self):
        plainte = PlainteFactory()
        assert plainte.numero_reference.startswith("PL-")
        assert len(plainte.numero_reference) == 14  # PL-YYYYMMDD-XXXX

    def test_numero_reference_unique(self):
        p1 = PlainteFactory()
        p2 = PlainteFactory()
        assert p1.numero_reference != p2.numero_reference

    def test_str(self):
        plainte = PlainteFactory(nom_plaignant="Marie Pierre")
        assert "Marie Pierre" in str(plainte)
        assert plainte.numero_reference in str(plainte)

    def test_statut_defaut(self):
        plainte = PlainteFactory()
        assert plainte.statut == "soumise"

    def test_membre_accuse_fk(self):
        accuse = MembreActifFactory()
        plainte = PlainteFactory(membre_accuse=accuse)
        assert plainte.membre_accuse == accuse

    def test_membre_accuse_optionnel(self):
        plainte = PlainteFactory(membre_accuse=None)
        assert plainte.membre_accuse is None


@pytest.mark.django_db
class TestNewsletter:
    def test_creation(self):
        n = NewsletterFactory()
        assert Newsletter.objects.filter(email=n.email).exists()

    def test_str(self):
        n = NewsletterFactory(email="test@cniah.ht")
        assert "test@cniah.ht" in str(n)


@pytest.mark.django_db
class TestMembreActif:
    def test_nom_complet(self):
        membre = MembreActifFactory(nom="PIERRE", prenom="Jean")
        assert "PIERRE" in membre.nom_complet
        assert "Jean" in membre.nom_complet

    def test_numero_unique(self):
        m1 = MembreActifFactory()
        m2 = MembreActifFactory()
        assert m1.numero != m2.numero

    def test_actif_par_defaut(self):
        membre = MembreActifFactory()
        assert membre.actif is True

    def test_email_public_optionnel(self):
        membre = MembreActifFactory()
        assert membre.email_public == ''

    def test_telephone_public_optionnel(self):
        membre = MembreActifFactory()
        assert membre.telephone_public == ''

    def test_email_public_stocke(self):
        membre = MembreActifFactory(email_public='contact@exemple.ht')
        assert membre.email_public == 'contact@exemple.ht'

    def test_telephone_public_stocke(self):
        membre = MembreActifFactory(telephone_public='+509 1234 5678')
        assert membre.telephone_public == '+509 1234 5678'


@pytest.mark.django_db
class TestCertificationDates:
    """F8 — Logique de dates : expiration le 30 septembre."""

    def test_expiration_meme_annee(self):
        # Délivré le 1er janvier → expire le 30 sept de la même année
        d = datetime.date(2025, 1, 1)
        exp = Certification.calculer_expiration(d, annees=1)
        assert exp == datetime.date(2025, 9, 30)

    def test_expiration_apres_sept_30(self):
        # Délivré le 1er octobre → expire le 30 sept de l'année suivante
        d = datetime.date(2025, 10, 1)
        exp = Certification.calculer_expiration(d, annees=1)
        assert exp == datetime.date(2026, 9, 30)

    def test_expiration_exactement_sept_30(self):
        # Délivré le 30 septembre → 30 sept n'est pas dépassé, expire le même 30 sept
        d = datetime.date(2025, 9, 30)
        exp = Certification.calculer_expiration(d, annees=1)
        assert exp == datetime.date(2025, 9, 30)

    def test_expiration_multiyear(self):
        # 3 ans depuis le 1er janvier 2025 → expire 30 sept 2027
        d = datetime.date(2025, 1, 1)
        exp = Certification.calculer_expiration(d, annees=3)
        assert exp == datetime.date(2027, 9, 30)

    def test_expiration_multiyear_apres_sept(self):
        # 2 ans depuis octobre 2025 → base est 2026, +1 → expire 30 sept 2027
        d = datetime.date(2025, 10, 15)
        exp = Certification.calculer_expiration(d, annees=2)
        assert exp == datetime.date(2027, 9, 30)

    def test_save_calcule_expiration_auto(self):
        membre = MembreActifFactory()
        cert = Certification(
            numero_certificat='TEST-001',
            membre=membre,
            date_delivrance=datetime.date(2025, 3, 1),
            annees_validite=2,
        )
        cert.save()
        assert cert.date_expiration == datetime.date(2026, 9, 30)

    def test_annees_validite_defaut_1(self):
        membre = MembreActifFactory()
        cert = Certification(
            numero_certificat='TEST-002',
            membre=membre,
            date_delivrance=datetime.date(2025, 5, 1),
        )
        cert.save()
        assert cert.annees_validite == 1
        assert cert.date_expiration == datetime.date(2025, 9, 30)


@pytest.mark.django_db
class TestConfigurationCertificat:
    """F5 — Singleton ConfigurationCertificat."""

    def test_singleton_get_creates(self):
        config = ConfigurationCertificat.get()
        assert config.pk == 1

    def test_singleton_get_idempotent(self):
        c1 = ConfigurationCertificat.get()
        c2 = ConfigurationCertificat.get()
        assert c1.pk == c2.pk == 1

    def test_save_force_pk_1(self):
        config = ConfigurationCertificat(nom_president='Test Président')
        config.save()
        assert config.pk == 1
        assert ConfigurationCertificat.objects.count() == 1
