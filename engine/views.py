from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    CalculatePriceInputSerializer,
    CalculatePriceOutputSerializer,
    CalculatePriceService,
)
from django.shortcuts import render
from django.views import View
from django import forms

class SimplePricingForm(forms.Form):
    ride_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    total_distance_km = forms.FloatField(min_value=0)
    total_ride_time_min = forms.IntegerField(min_value=0)
    waiting_time_min = forms.IntegerField(min_value=0)

class PricingDashboardView(View):
    template_name = 'engine/pricing_dashboard.html'

    def get(self, request):
        form = SimplePricingForm()
        return render(request, self.template_name, {'form': form, 'result': None})

    def post(self, request):
        form = SimplePricingForm(request.POST)
        result = None
        error = None
        if form.is_valid():
            data = form.cleaned_data
            from .services import calculate_price, PricingCalculationError
            try:
                result = calculate_price(
                    ride_date=str(data['ride_date']),
                    total_distance_km=data['total_distance_km'],
                    total_ride_time_min=data['total_ride_time_min'],
                    waiting_time_min=data['waiting_time_min'],
                )
            except PricingCalculationError as e:
                error = str(e)
        return render(request, self.template_name, {'form': form, 'result': result, 'error': error})

class CalculatePriceAPIView(APIView):
    """
    Calculate ride price based on given inputs.
    """
    @swagger_auto_schema(request_body=CalculatePriceInputSerializer, responses={200: CalculatePriceOutputSerializer})
    def post(self, request):
        serializer = CalculatePriceInputSerializer(data=request.data)
        if serializer.is_valid():
            result, error = CalculatePriceService.calculate(serializer.validated_data)
            if error:
                return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)
            output_serializer = CalculatePriceOutputSerializer(result)
            return Response(output_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
