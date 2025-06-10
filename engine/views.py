from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    CalculatePriceInputSerializer,
    CalculatePriceOutputSerializer,
    CalculatePriceService,
)

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
