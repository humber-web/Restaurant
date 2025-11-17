"""
Views for common app - company settings and tax configuration.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import date

from .permissions import IsManager
from .models import CompanySettings, TaxRate
from .serializers import CompanySettingsSerializer, TaxRateSerializer


class CompanySettingsView(APIView):
    """
    Get or update company settings (singleton).
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get company settings"""
        settings = CompanySettings.get_instance()
        serializer = CompanySettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        """Update company settings"""
        settings = CompanySettings.get_instance()
        serializer = CompanySettingsSerializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'detail': 'Configuracoes atualizadas com sucesso',
                'data': serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaxRateListView(APIView):
    """
    List all tax rates or create a new one.
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """
        List all tax rates.
        Optional query parameters:
        - active_only: true/false (default: false)
        - tax_code: filter by tax code (NOR, RED, ISE, OUT)
        """
        tax_rates = TaxRate.objects.all()

        # Filter by active status
        if request.query_params.get('active_only') == 'true':
            tax_rates = tax_rates.filter(is_active=True)

        # Filter by tax code
        tax_code = request.query_params.get('tax_code')
        if tax_code:
            tax_rates = tax_rates.filter(tax_code=tax_code)

        serializer = TaxRateSerializer(tax_rates, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new tax rate"""
        serializer = TaxRateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'detail': 'Taxa de IVA criada com sucesso',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaxRateDetailView(APIView):
    """
    Retrieve, update or delete a specific tax rate.
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        """Get tax rate details"""
        tax_rate = get_object_or_404(TaxRate, pk=pk)
        serializer = TaxRateSerializer(tax_rate)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update tax rate"""
        tax_rate = get_object_or_404(TaxRate, pk=pk)
        serializer = TaxRateSerializer(tax_rate, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'detail': 'Taxa de IVA atualizada com sucesso',
                'data': serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete tax rate"""
        tax_rate = get_object_or_404(TaxRate, pk=pk)
        tax_rate.delete()
        return Response({
            'detail': 'Taxa de IVA eliminada com sucesso'
        }, status=status.HTTP_204_NO_CONTENT)


class ActiveTaxRateView(APIView):
    """
    Get the currently active tax rate for a given tax code.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get active tax rate.
        Query parameters:
        - tax_code: Tax code (default: NOR)
        - as_of_date: Date in YYYY-MM-DD format (default: today)
        """
        tax_code = request.query_params.get('tax_code', 'NOR')
        as_of_date_str = request.query_params.get('as_of_date')

        if as_of_date_str:
            try:
                from datetime import datetime
                as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({
                    'error': 'Formato de data invalido. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            as_of_date = date.today()

        tax_rate = TaxRate.get_active_rate(tax_code=tax_code, as_of_date=as_of_date)

        if not tax_rate:
            return Response({
                'error': f'Nenhuma taxa ativa encontrada para {tax_code} em {as_of_date}',
                'fallback': {
                    'percentage': 15.00,
                    'description': 'Taxa padrao (nao configurada)'
                }
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TaxRateSerializer(tax_rate)
        return Response(serializer.data)
