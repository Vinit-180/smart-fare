from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import PricingConfig, DistanceBasePrice, DistanceAdditionalPrice, TimeMultiplierSlab, WaitingCharge
from .services import calculate_price, PricingCalculationError
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class PricingServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.config = PricingConfig.objects.create(name="Test Config", is_active=True, created_by=self.user)
        DistanceBasePrice.objects.create(config=self.config, weekday="monday", up_to_kms=5, price=100)
        DistanceAdditionalPrice.objects.create(config=self.config, per_km_price=20)
        TimeMultiplierSlab.objects.create(config=self.config, from_minutes=60, to_minutes=120, multiplier=1.5)
        WaitingCharge.objects.create(config=self.config, free_minutes=5, charge_per_slab=10, slab_minutes=5)

    def test_calculate_price_normal(self):
        result = calculate_price("2025-06-09", 7.5, 75, 10)  # Monday
        self.assertEqual(result["base_price"], 100.0)
        self.assertEqual(result["additional_distance_charge"], 50.0)  # (7.5-5)*20
        self.assertEqual(result["time_multiplier_charge"], 225.0)  # (100+50)*1.5
        self.assertEqual(result["waiting_charge"], 10.0)  # (10-5)//5=1 slab
        self.assertEqual(result["final_price"], 385.0)

    def test_calculate_price_zero_distance(self):
        result = calculate_price("2025-06-09", 0, 75, 10)
        self.assertEqual(result["base_price"], 0.0)
        self.assertEqual(result["final_price"], result["time_multiplier_charge"] + result["waiting_charge"])

    def test_calculate_price_no_active_config(self):
        self.config.is_active = False
        self.config.save()
        with self.assertRaises(PricingCalculationError):
            calculate_price("2025-06-09", 7.5, 75, 10)

    def test_calculate_price_no_dbp_for_weekday(self):
        # Remove Monday DBP
        DistanceBasePrice.objects.filter(config=self.config, weekday="monday").delete()
        with self.assertRaises(PricingCalculationError):
            calculate_price("2025-06-09", 7.5, 75, 10)

class PricingAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='apitestuser')
        self.config = PricingConfig.objects.create(name="API Config", is_active=True, created_by=self.user)
        DistanceBasePrice.objects.create(config=self.config, weekday="tuesday", up_to_kms=5, price=90)
        DistanceAdditionalPrice.objects.create(config=self.config, per_km_price=15)
        TimeMultiplierSlab.objects.create(config=self.config, from_minutes=60, to_minutes=120, multiplier=2.0)
        WaitingCharge.objects.create(config=self.config, free_minutes=5, charge_per_slab=5, slab_minutes=5)
        self.client = APIClient()

    def test_api_calculate_price_success(self):
        url = reverse('calculate-price')
        data = {
            "ride_date": "2025-06-10",  # Tuesday
            "total_distance_km": 10,
            "total_ride_time_min": 75,
            "waiting_time_min": 10
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("final_price", response.data)

    def test_api_no_active_config(self):
        self.config.is_active = False
        self.config.save()
        url = reverse('calculate-price')
        data = {
            "ride_date": "2025-06-10",
            "total_distance_km": 10,
            "total_ride_time_min": 75,
            "waiting_time_min": 10
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)
