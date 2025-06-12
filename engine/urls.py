from django.urls import path
from .views import CalculatePriceAPIView, PricingDashboardView

urlpatterns = [
    path('api/calculate-price/', CalculatePriceAPIView.as_view(), name='calculate-price'),
    path('dashboard/', PricingDashboardView.as_view(), name='pricing-dashboard'),
]
