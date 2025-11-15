# api/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # NEW: Modular apps
    path('api/', include('apps.users.urls')),         # User management & authentication
    path('api/', include('apps.menu.urls')),          # Menu categories & items
    path('api/', include('apps.tables.urls')),        # Table management
    path('api/', include('apps.inventory.urls')),     # Inventory management
    path('api/', include('apps.orders.urls')),        # Order management (Premium)
    path('api/', include('apps.payments.urls')),      # Payment processing (Premium)
    path('api/', include('apps.cash_register.urls')), # Cash register (Premium)
    path('api/', include('apps.audit.urls')),         # Audit logs
]
