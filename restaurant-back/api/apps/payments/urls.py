"""
Payment Processing URL Configuration
"""
from django.urls import path
from .views import (
    ListPaymentsView,
    PaymentDetailView,
    ProcessPaymentView,
    DeletePaymentView
)

urlpatterns = [
    # List all payments
    path('payments/', ListPaymentsView.as_view(), name='list-payments'),

    # Process payment (create)
    path('payment/process/', ProcessPaymentView.as_view(), name='process-payment'),

    # Get payment by ID
    path('payment/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),

    # Search payments (without pk)
    path('payment/', PaymentDetailView.as_view(), name='search-payments'),

    # Delete payment
    path('payment/<int:pk>/delete/', DeletePaymentView.as_view(), name='delete-payment'),
]
