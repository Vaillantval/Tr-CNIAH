import pytest
import datetime
from .factories import AdvertisementFactory, ExpiredAdvertisementFactory, FutureAdvertisementFactory


@pytest.mark.django_db
class TestAdvertisement:
    def test_is_valid_active_today(self):
        ad = AdvertisementFactory()
        assert ad.is_valid() is True

    def test_is_valid_expired(self):
        ad = ExpiredAdvertisementFactory()
        assert ad.is_valid() is False

    def test_is_valid_future(self):
        ad = FutureAdvertisementFactory()
        assert ad.is_valid() is False

    def test_is_valid_inactive(self):
        ad = AdvertisementFactory(is_active=False)
        assert ad.is_valid() is False

    def test_str(self):
        ad = AdvertisementFactory(title="Pub test", position='banner')
        assert "Pub test" in str(ad)
        assert "banner" in str(ad)

    def test_position_choices(self):
        for position in ('banner', 'sidebar', 'footer'):
            ad = AdvertisementFactory(position=position)
            assert ad.position == position
