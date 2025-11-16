"""
Customer API Views
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from apps.common.permissions import IsManager
from .models import Customer
from .serializers import CustomerSerializer, CustomerListSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer CRUD operations.

    Endpoints:
    - GET    /api/customers/          - List all customers
    - POST   /api/customers/          - Create customer
    - GET    /api/customers/<id>/     - Get customer details
    - PUT    /api/customers/<id>/     - Update customer
    - DELETE /api/customers/<id>/     - Delete customer (soft delete)
    - GET    /api/customers/search/?q=<query>  - Search customers
    """
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['tax_id', 'company_name', 'first_name', 'last_name', 'email']
    ordering_fields = ['customerID', 'company_name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Use lightweight serializer for list action
        """
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_queryset(self):
        """
        Filter customers based on query parameters
        """
        queryset = super().get_queryset()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by customer type
        customer_type = self.request.query_params.get('customer_type')
        if customer_type:
            queryset = queryset.filter(customer_type=customer_type)

        # Search query
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(tax_id__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
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
        Search customer by exact NIF match.
        GET /api/customers/search_by_nif/?nif=123456789
        """
        nif = request.query_params.get('nif')
        if not nif:
            return Response(
                {'error': 'NIF parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = Customer.objects.get(tax_id=nif)
            serializer = self.get_serializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Cliente não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        List only active customers.
        GET /api/customers/active/
        """
        active_customers = self.get_queryset().filter(is_active=True)
        page = self.paginate_queryset(active_customers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(active_customers, many=True)
        return Response(serializer.data)
