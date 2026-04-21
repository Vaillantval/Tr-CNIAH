import pytest
from apps.core.models import Plainte, Newsletter, MembreActif
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
