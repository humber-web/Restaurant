"""
Feature Flag System for Module-based Licensing
Allows enabling/disabling modules based on customer subscription.
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


# ==================== AVAILABLE MODULES ====================
class Modules:
    """Available modules that can be enabled/disabled."""
    USERS = 'users'
    MENU = 'menu'
    TABLES = 'tables'
    INVENTORY = 'inventory'
    ORDERS = 'orders'           # May require extra cost
    PAYMENTS = 'payments'       # May require extra cost
    CASH_REGISTER = 'cash_register'  # May require extra cost
    AUDIT = 'audit'
    ANALYTICS = 'analytics'     # Future module


# ==================== MODULE CONFIGURATIONS ====================
# Define which modules require payment/subscription
PREMIUM_MODULES = {
    Modules.INVENTORY: {
        'name': 'Inventory Management',
        'description': 'Advanced inventory tracking with stock alerts and overselling management',
        'price': 30.00,  # Monthly price
        'requires': [Modules.MENU]  # Dependencies
    },
    Modules.ANALYTICS: {
        'name': 'Advanced Analytics',
        'description': 'Sales reports, business insights, and performance dashboards',
        'price': 40.00,
        'requires': [Modules.ORDERS]
    }
}

# Free modules (always enabled) - Core restaurant features
FREE_MODULES = [
    Modules.USERS,
    Modules.MENU,
    Modules.TABLES,
    Modules.ORDERS,           # Core feature - FREE
    Modules.PAYMENTS,         # Core feature - FREE
    Modules.CASH_REGISTER,    # Core feature - FREE
    Modules.AUDIT
]


# ==================== FEATURE FLAG STORAGE ====================
class FeatureFlags:
    """
    Feature flag management.
    
    In production, this should be stored in:
    - Database (per organization/tenant)
    - Redis (for fast access)
    - Environment variables (for deployment-wide settings)
    
    For now, we'll use settings-based configuration.
    """
    
    @staticmethod
    def is_module_enabled(module_name, organization_id=None):
        """
        Check if a module is enabled for the organization.

        Args:
            module_name: Module identifier (e.g., 'orders')
            organization_id: Organization ID (for multi-tenant)

        Returns:
            bool: True if module is enabled
        """
        # Free modules are always enabled
        if module_name in FREE_MODULES:
            return True

        # Check if it's a premium module
        if module_name in PREMIUM_MODULES:
            # Check database for module subscription
            try:
                from apps.common.models import ModuleSubscription
                from django.utils import timezone

                subscription = ModuleSubscription.objects.filter(
                    module_name=module_name
                ).first()

                if not subscription:
                    # No subscription record - disabled by default
                    return False

                # Check if subscription is active and not expired
                if not subscription.is_enabled:
                    return False

                if subscription.expires_at and subscription.expires_at < timezone.now():
                    return False

                return True

            except Exception:
                # If database not ready or error, fall back to settings
                from django.conf import settings
                enabled_modules = getattr(settings, 'ENABLED_MODULES', FREE_MODULES)
                return module_name in enabled_modules

        # Unknown module - disabled by default
        return False
    
    @staticmethod
    def get_enabled_modules(organization_id=None):
        """Get list of enabled modules for an organization."""
        from django.conf import settings
        return getattr(settings, 'ENABLED_MODULES', FREE_MODULES)
    
    @staticmethod
    def get_module_info(module_name):
        """Get information about a module."""
        if module_name in PREMIUM_MODULES:
            return PREMIUM_MODULES[module_name]
        return None
    
    @staticmethod
    def check_dependencies(module_name):
        """
        Check if all required modules are enabled.
        
        Returns:
            tuple: (bool, list) - (all_satisfied, missing_modules)
        """
        if module_name not in PREMIUM_MODULES:
            return True, []
        
        required = PREMIUM_MODULES[module_name].get('requires', [])
        missing = [mod for mod in required if not FeatureFlags.is_module_enabled(mod)]
        
        return len(missing) == 0, missing


# ==================== VIEW DECORATOR ====================
def require_module(module_name):
    """
    Decorator to protect views that require a specific module.
    
    Usage:
        @require_module(Modules.ORDERS)
        class CreateOrderView(APIView):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if module is enabled
            if not FeatureFlags.is_module_enabled(module_name):
                return Response({
                    'error': 'Module not enabled',
                    'module': module_name,
                    'message': f'The {module_name} module is not enabled for your account.',
                    'contact': 'Please contact support to enable this feature.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check dependencies
            satisfied, missing = FeatureFlags.check_dependencies(module_name)
            if not satisfied:
                return Response({
                    'error': 'Missing dependencies',
                    'module': module_name,
                    'missing_modules': missing,
                    'message': f'This module requires: {", ".join(missing)}'
                }, status=status.HTTP_424_FAILED_DEPENDENCY)
            
            # Module is enabled, proceed with the view
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== CLASS-BASED VIEW MIXIN ====================
class RequireModuleMixin:
    """
    Mixin for class-based views that require a specific module.
    
    Usage:
        class CreateOrderView(RequireModuleMixin, APIView):
            required_module = Modules.ORDERS
            ...
    """
    required_module = None
    
    def dispatch(self, request, *args, **kwargs):
        if self.required_module:
            # Check if module is enabled
            if not FeatureFlags.is_module_enabled(self.required_module):
                return Response({
                    'error': 'Module not enabled',
                    'module': self.required_module,
                    'message': f'The {self.required_module} module is not enabled for your account.',
                    'contact': 'Please contact support to enable this feature.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check dependencies
            satisfied, missing = FeatureFlags.check_dependencies(self.required_module)
            if not satisfied:
                return Response({
                    'error': 'Missing dependencies',
                    'module': self.required_module,
                    'missing_modules': missing,
                    'message': f'This module requires: {", ".join(missing)}'
                }, status=status.HTTP_424_FAILED_DEPENDENCY)
        
        return super().dispatch(request, *args, **kwargs)
