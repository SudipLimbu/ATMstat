from django.test import SimpleTestCase
from django.urls import reverse, resolve
from transactions.views import get_eod_data, ForecastView, DepositMoneyView
from core.views import HomeView


class TestUrls(SimpleTestCase):
    def test_home_url(self):
        url = reverse("home")
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, HomeView)

    def test_home_url(self):
        url = reverse("deposit_money")
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, DepositMoneyView)

    def test_home_url(self):
        url = reverse("Forecast")
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, ForecastView)
