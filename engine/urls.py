from django.urls import path
from .views import CalculatePriceAPIView

urlpatterns = [
    path('api/calculate-price/', CalculatePriceAPIView.as_view(), name='calculate-price'),
]
