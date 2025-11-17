"""
Supplier API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet

# Router for ViewSet
router = DefaultRouter()
router.register(r'', SupplierViewSet, basename='supplier')

urlpatterns = [
    path('', include(router.urls)),
]
