import factory
import datetime
from django.utils import timezone
from apps.advertisements.models import Advertisement


class AdvertisementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Advertisement

    title = factory.Sequence(lambda n: f"Publicité {n}")
    image = factory.django.ImageField(color='blue')
    position = 'banner'
    start_date = factory.LazyFunction(lambda: datetime.date.today())
    end_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=30)
    )
    is_active = True


class ExpiredAdvertisementFactory(AdvertisementFactory):
    start_date = factory.LazyFunction(
        lambda: datetime.date.today() - datetime.timedelta(days=60)
    )
    end_date = factory.LazyFunction(
        lambda: datetime.date.today() - datetime.timedelta(days=1)
    )


class FutureAdvertisementFactory(AdvertisementFactory):
    start_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=1)
    )
    end_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=30)
    )
