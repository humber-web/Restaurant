"""
URL patterns for common app - company settings and tax configuration.
"""
from django.urls import path
from .views import (
    CompanySettingsView,
    TaxRateListView,
    TaxRateDetailView,
    ActiveTaxRateView,
)

urlpatterns = [
    # Company Settings (singleton)
    path('company-settings/', CompanySettingsView.as_view(), name='company-settings'),

    # Tax Rates
    path('tax-rates/', TaxRateListView.as_view(), name='tax-rates-list'),
    path('tax-rates/<int:pk>/', TaxRateDetailView.as_view(), name='tax-rate-detail'),
    path('tax-rates/active/', ActiveTaxRateView.as_view(), name='tax-rate-active'),
]
