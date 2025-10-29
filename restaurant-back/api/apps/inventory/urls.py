"""
Inventory Management URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('inventory_item/register/', views.CreateInventoryItemView.as_view(), name='inventory-create'),
    path('inventory_item/', views.InventoryItemListView.as_view(), name='inventory-list'),
    path('inventory_item/<int:pk>/', views.InventoryItemDetailView.as_view(), name='inventory-detail'),
    path('inventory_item/search/', views.InventoryItemDetailView.as_view(), name='inventory-search'),
    path('inventory_item/<int:pk>/update/', views.InventoryItemUpdateView.as_view(), name='inventory-update'),
    path('inventory_item/<int:pk>/delete/', views.InventoryItemDeleteView.as_view(), name='inventory-delete'),
]
