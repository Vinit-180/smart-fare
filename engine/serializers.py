from rest_framework import serializers
from .services import calculate_price, PricingCalculationError

class CalculatePriceInputSerializer(serializers.Serializer):
    ride_date = serializers.DateField()
    total_distance_km = serializers.FloatField(min_value=0)
    total_ride_time_min = serializers.IntegerField(min_value=0)
    waiting_time_min = serializers.IntegerField(min_value=0)

class CalculatePriceOutputSerializer(serializers.Serializer):
    base_price = serializers.FloatField()
    additional_distance_charge = serializers.FloatField()
    time_multiplier_charge = serializers.FloatField()
    waiting_charge = serializers.FloatField()
    final_price = serializers.FloatField()

class CalculatePriceService:
    @staticmethod
    def calculate(validated_data):
        try:
            result = calculate_price(
                ride_date=str(validated_data['ride_date']),
                total_distance_km=validated_data['total_distance_km'],
                total_ride_time_min=validated_data['total_ride_time_min'],
                waiting_time_min=validated_data['waiting_time_min']
            )
            return result, None
        except PricingCalculationError as e:
            return None, str(e)
