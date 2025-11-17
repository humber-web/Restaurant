from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperationLogViewSet

router = DefaultRouter()
router.register(r'audit/logs', OperationLogViewSet, basename='audit-logs')

urlpatterns = [
    path('', include(router.urls)),
]
