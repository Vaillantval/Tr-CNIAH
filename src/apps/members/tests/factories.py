import factory
from django.utils.crypto import get_random_string
from apps.members.models import User, Cotisation, ForumCategorie, ForumSujet
from apps.core.tests.factories import MembreActifFactory
import datetime


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@cniah.ht")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123!')
    first_name = "Jean"
    last_name = "Baptiste"
    email_verified = True
    membre_actif = factory.SubFactory(MembreActifFactory)


class UnverifiedUserFactory(UserFactory):
    email_verified = False
    email_verification_token = factory.LazyFunction(lambda: get_random_string(50))


class CotisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cotisation

    user = factory.SubFactory(UserFactory)
    montant = 5000.00
    date_debut = factory.LazyFunction(lambda: datetime.date.today())
    date_fin = factory.LazyFunction(
        lambda: datetime.date.today().replace(year=datetime.date.today().year + 1)
    )
    statut = "en_attente"


class ForumCategorieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForumCategorie

    nom = factory.Sequence(lambda n: f"Catégorie Forum {n}")
    description = "Description de la catégorie."


class ForumSujetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForumSujet

    categorie = factory.SubFactory(ForumCategorieFactory)
    auteur = factory.SubFactory(UserFactory)
    titre = factory.Sequence(lambda n: f"Sujet de test {n}")
    contenu = "Contenu du sujet de test pour vérification."
