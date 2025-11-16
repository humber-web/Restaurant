"""
Supplier API Views
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from apps.common.permissions import IsManager
from .models import Supplier
from .serializers import SupplierSerializer, SupplierListSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Supplier CRUD operations.

    Endpoints:
    - GET    /api/suppliers/          - List all suppliers
    - POST   /api/suppliers/          - Create supplier
    - GET    /api/suppliers/<id>/     - Get supplier details
    - PUT    /api/suppliers/<id>/     - Update supplier
    - DELETE /api/suppliers/<id>/     - Delete supplier (soft delete)
    - GET    /api/suppliers/search/?q=<query>  - Search suppliers
    """
    queryset = Supplier.objects.all()
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['tax_id', 'company_name', 'email']
    ordering_fields = ['supplierID', 'company_name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Use lightweight serializer for list action
        """
        if self.action == 'list':
            return SupplierListSerializer
        return SupplierSerializer

    def get_queryset(self):
        """
        Filter suppliers based on query parameters
        """
        queryset = super().get_queryset()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Search query
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(tax_id__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        return queryset

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - set is_active to False instead of deleting
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def search_by_nif(self, request):
        """
        Search supplier by exact NIF match.
        GET /api/suppliers/search_by_nif/?nif=123456789
        """
        nif = request.query_params.get('nif')
        if not nif:
            return Response(
                {'error': 'NIF parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            supplier = Supplier.objects.get(tax_id=nif)
            serializer = self.get_serializer(supplier)
            return Response(serializer.data)
        except Supplier.DoesNotExist:
            return Response(
                {'error': 'Fornecedor não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        List only active suppliers.
        GET /api/suppliers/active/
        """
        active_suppliers = self.get_queryset().filter(is_active=True)
        page = self.paginate_queryset(active_suppliers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(active_suppliers, many=True)
        return Response(serializer.data)
