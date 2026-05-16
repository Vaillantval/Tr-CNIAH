import datetime
import factory
from apps.core.models import (
    TitreProfessionnel, MembreActif, Certification, Plainte, Newsletter,
    DocumentCategory, ReferenceDocument,
)


class TitreProfessionnelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TitreProfessionnel

    nom = factory.Sequence(lambda n: f"Ingénieur Civil {n}")
    abreviation = factory.Sequence(lambda n: f"IC{n}")


class MembreActifFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembreActif

    numero = factory.Sequence(lambda n: f"CNIAH-{n:04d}")
    nom = factory.Sequence(lambda n: f"NOM{n}")
    prenom = factory.Sequence(lambda n: f"Prénom{n}")
    email = factory.Sequence(lambda n: f"membre{n}@cniah.ht")
    titre = factory.SubFactory(TitreProfessionnelFactory)
    actif = True


class CertificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certification

    numero_certificat = factory.Sequence(lambda n: f"CNIAH-CERT-{n:04d}")
    membre = factory.SubFactory(MembreActifFactory)
    date_delivrance = factory.LazyFunction(lambda: datetime.date.today())
    annees_validite = 1
    statut = 'valide'


class PlainteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plainte

    nom_plaignant = "Jean Dupont"
    email_plaignant = "jean@test.com"
    telephone = "50912345678"
    membre_accuse = factory.SubFactory(MembreActifFactory)
    type_plainte = "ethique"
    description = "Description détaillée de la plainte pour test."


class NewsletterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Newsletter

    email = factory.Sequence(lambda n: f"newsletter{n}@test.com")


class DocumentCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentCategory

    name = factory.Sequence(lambda n: f"Catégorie {n}")
    slug = factory.Sequence(lambda n: f"categorie-{n}")


class ReferenceDocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReferenceDocument

    title = factory.Sequence(lambda n: f"Document {n}")
    slug = factory.Sequence(lambda n: f"document-{n}")
    category = factory.SubFactory(DocumentCategoryFactory)
    description = "Description du document."
    file = factory.django.FileField(filename="test.pdf", data=b"%PDF-1.4 test")
    file_type = "pdf"
