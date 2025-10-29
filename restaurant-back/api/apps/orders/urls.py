"""
Order Management URL Configuration
"""
from django.urls import path
from .views import (
    ListOrdersView,
    OrderDetailView,
    CreateOrderView,
    UpdateOrderItemsView,
    TransferOrderItemsView,
    DeleteOrderView
)

urlpatterns = [
    # List all orders
    path('orders/', ListOrdersView.as_view(), name='list-orders'),

    # Create order
    path('order/register/', CreateOrderView.as_view(), name='create-order'),

    # Get order by ID
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    # Search orders (without pk)
    path('order/', OrderDetailView.as_view(), name='search-orders'),

    # Update order items
    path('order/<int:pk>/update/', UpdateOrderItemsView.as_view(), name='update-order'),

    # Transfer items between orders
    path('order/transfer/', TransferOrderItemsView.as_view(), name='transfer-order-items'),

    # Delete order
    path('order/<int:pk>/delete/', DeleteOrderView.as_view(), name='delete-order'),
]
