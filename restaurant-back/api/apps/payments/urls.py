"""
Payment Processing URL Configuration
"""
from django.urls import path
from .views import (
    ListPaymentsView,
    PaymentDetailView,
    ProcessPaymentView,
    DeletePaymentView,
    SignInvoiceView,
    ExportSAFTView,
    ValidateInvoiceHashView,
    GenerateEFaturaView,
    DownloadEFaturaXMLView,
    SignAndSubmitEFaturaView,
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

    # ===== FISCAL COMPLIANCE ENDPOINTS (SAF-T CV / e-Fatura) =====

    # Sign invoice (generate fiscal fields)
    path('payment/<int:pk>/sign/', SignInvoiceView.as_view(), name='sign-invoice'),

    # Export SAF-T CV
    path('saft/export/', ExportSAFTView.as_view(), name='export-saft'),

    # Validate invoice hash
    path('payment/<int:pk>/validate-hash/', ValidateInvoiceHashView.as_view(), name='validate-hash'),

    # ===== E-FATURA CV ENDPOINTS (Real-time Electronic Invoicing) =====

    # Sign and submit e-Fatura (recommended - all in one)
    path('payment/<int:pk>/efatura/submit/', SignAndSubmitEFaturaView.as_view(), name='efatura-sign-submit'),

    # Generate e-Fatura XML (requires already signed invoice)
    path('payment/<int:pk>/efatura/generate/', GenerateEFaturaView.as_view(), name='efatura-generate'),

    # Download e-Fatura XML
    path('payment/<int:pk>/efatura/download/', DownloadEFaturaXMLView.as_view(), name='efatura-download'),
]
