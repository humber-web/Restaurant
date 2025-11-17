"""
URL Configuration for Purchase Orders and Supplier Invoices
"""
from django.urls import path
from .views import (
    PurchaseOrderListView,
    PurchaseOrderDetailView,
    ReceiveGoodsView,
    SupplierInvoiceListView,
    SupplierInvoiceDetailView,
    MarkInvoiceAsPaidView
)

urlpatterns = [
    # Purchase Orders
    path('purchase-orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('purchase-orders/<int:pk>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),

    # Goods Receipt
    path('receive-goods/', ReceiveGoodsView.as_view(), name='receive-goods'),

    # Supplier Invoices
    path('supplier-invoices/', SupplierInvoiceListView.as_view(), name='supplier-invoice-list'),
    path('supplier-invoices/<int:pk>/', SupplierInvoiceDetailView.as_view(), name='supplier-invoice-detail'),
    path('supplier-invoices/<int:pk>/mark-paid/', MarkInvoiceAsPaidView.as_view(), name='mark-invoice-paid'),
]
