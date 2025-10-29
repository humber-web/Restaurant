"""
Cash Register Management URL Configuration
"""
from django.urls import path
from .views import (
    ListCashRegistersView,
    CashRegisterDetailView,
    StartCashRegisterView,
    CloseCashRegisterView,
    CashRegisterSummaryView,
    InsertMoneyView,
    ExtractMoneyView
)

urlpatterns = [
    # List all cash registers
    path('cash_registers/', ListCashRegistersView.as_view(), name='list-cash-registers'),

    # Start new cash register
    path('cash_register/start/', StartCashRegisterView.as_view(), name='start-cash-register'),

    # Close cash register
    path('cash_register/close/', CloseCashRegisterView.as_view(), name='close-cash-register'),

    # Get summary of last closed register
    path('cash_register/summary/', CashRegisterSummaryView.as_view(), name='cash-register-summary'),

    # Insert money
    path('cash_register/insert/', InsertMoneyView.as_view(), name='insert-money'),

    # Extract money
    path('cash_register/extract/', ExtractMoneyView.as_view(), name='extract-money'),

    # Get cash register by ID
    path('cash_register/<int:pk>/', CashRegisterDetailView.as_view(), name='cash-register-detail'),

    # Search cash registers (without pk)
    path('cash_register/', CashRegisterDetailView.as_view(), name='search-cash-registers'),
]
