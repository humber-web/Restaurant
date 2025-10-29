"""
Cash Register Management Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import CashRegister
from .serializers import (
    CashRegisterSummarySerializer,
    StartCashRegisterSerializer,
    InsertMoneySerializer,
    ExtractMoneySerializer
)
from apps.common.permissions import IsManager


class ListCashRegistersView(APIView):
    """
    List all cash registers.
    Requires: cash_register module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get all cash registers ordered by start time."""
        cash_registers = CashRegister.objects.all().order_by('-start_time')
        serializer = CashRegisterSummarySerializer(cash_registers, many=True)
        return Response(serializer.data)


class CashRegisterDetailView(APIView):
    """
    Get cash register detail by ID or search.
    Requires: cash_register module + authentication
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Get cash register by ID or search by filters.

        Query parameters:
        - user: Filter by user ID
        - is_open: Filter by open status (true/false)
        """
        if pk:
            # Get specific cash register
            cash_register = get_object_or_404(CashRegister, pk=pk)

            # Verify user can access this register
            if not request.user.is_staff and cash_register.user != request.user:
                return Response({
                    'error': 'You do not have permission to view this cash register.'
                }, status=status.HTTP_403_FORBIDDEN)

            serializer = CashRegisterSummarySerializer(cash_register)
            return Response(serializer.data)
        else:
            # Search cash registers
            user_id = request.query_params.get('user')
            is_open = request.query_params.get('is_open')

            queryset = CashRegister.objects.all()

            # Non-staff users can only see their own registers
            if not request.user.is_staff:
                queryset = queryset.filter(user=request.user)

            if user_id:
                queryset = queryset.filter(user__id=user_id)
            if is_open is not None:
                is_open_bool = is_open.lower() == 'true'
                queryset = queryset.filter(is_open=is_open_bool)

            serializer = CashRegisterSummarySerializer(queryset, many=True)
            return Response(serializer.data)


class StartCashRegisterView(APIView):
    """
    Start a new cash register session.
    Requires: cash_register module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Start a new cash register session.

        Request body:
        {
            "initial_amount": 100.00
        }
        """
        # Check if user already has an open register
        existing_register = CashRegister.objects.filter(
            user=request.user,
            is_open=True
        ).first()

        if existing_register:
            return Response({
                'error': 'You already have an open cash register.',
                'cash_register_id': existing_register.id,
                'started_at': existing_register.start_time
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate input
        serializer = StartCashRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        initial_amount = serializer.validated_data['initial_amount']

        # Create new cash register
        cash_register = CashRegister.objects.create(
            user=request.user,
            initial_amount=initial_amount,
            final_amount=initial_amount
        )

        return Response({
            'detail': 'Cash register started successfully.',
            'cash_register_id': cash_register.id,
            'initial_amount': str(cash_register.initial_amount),
            'started_at': cash_register.start_time
        }, status=status.HTTP_201_CREATED)


class CloseCashRegisterView(APIView):
    """
    Close the current user's cash register session.
    Requires: cash_register module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Close cash register and calculate differences.

        Request body:
        {
            "declared_cash": 250.00,
            "declared_card": 150.00
        }
        """
        # Find user's open register
        cash_register = CashRegister.objects.filter(
            user=request.user,
            is_open=True
        ).first()

        if not cash_register:
            return Response({
                'error': 'No open cash register found.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get declared amounts
        try:
            declared_cash = Decimal(str(request.data.get('declared_cash', 0)))
            declared_card = Decimal(str(request.data.get('declared_card', 0)))
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount format for declared_cash or declared_card.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Close register and get results
        results = cash_register.close_register(declared_cash, declared_card)

        return Response({
            'detail': 'Cash register closed successfully.',
            'results': {
                'expected_cash': str(results['expected_cash']),
                'declared_cash': str(results['declared_cash']),
                'cash_difference': str(results['cash_difference']),
                'expected_card': str(results['expected_card']),
                'declared_card': str(results['declared_card']),
                'card_difference': str(results['card_difference']),
            },
            'closed_at': cash_register.end_time
        }, status=status.HTTP_200_OK)


class CashRegisterSummaryView(APIView):
    """
    Get summary of the last closed cash register.
    Requires: cash_register module + authentication
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get summary of user's last closed cash register."""
        cash_register = CashRegister.objects.filter(
            user=request.user,
            is_open=False
        ).order_by('-end_time').first()

        if not cash_register:
            return Response({
                'error': 'No closed cash register data found for this user.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CashRegisterSummarySerializer(cash_register)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InsertMoneyView(APIView):
    """
    Insert money into the current cash register.
    Requires: cash_register module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Insert money into cash register.

        Request body:
        {
            "amount": 50.00
        }
        """
        serializer = InsertMoneySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data['amount']

        # Find user's open register
        cash_register = CashRegister.objects.filter(
            user=request.user,
            is_open=True
        ).first()

        if not cash_register:
            return Response({
                'error': 'No open cash register found for this user.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Insert money
        cash_register.insert_money(amount)

        return Response({
            'detail': 'Money inserted successfully.',
            'amount': str(amount),
            'new_final_amount': str(cash_register.final_amount)
        }, status=status.HTTP_200_OK)


class ExtractMoneyView(APIView):
    """
    Extract money from the current cash register.
    Requires: cash_register module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Extract money from cash register.

        Request body:
        {
            "amount": 50.00
        }
        """
        serializer = ExtractMoneySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data['amount']

        # Find user's open register
        cash_register = CashRegister.objects.filter(
            user=request.user,
            is_open=True
        ).first()

        if not cash_register:
            return Response({
                'error': 'No open cash register found for this user.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check sufficient funds
        current_amount = cash_register.final_amount or cash_register.initial_amount
        if current_amount < amount:
            return Response({
                'error': 'Insufficient funds in cash register.',
                'current_amount': str(current_amount),
                'requested_amount': str(amount)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract money
        cash_register.extract_money(amount)

        return Response({
            'detail': 'Money extracted successfully.',
            'amount': str(amount),
            'new_final_amount': str(cash_register.final_amount)
        }, status=status.HTTP_200_OK)
