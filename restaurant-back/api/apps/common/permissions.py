"""
Shared permission classes for the Restaurant Management System.
"""
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsManager(BasePermission):
    """
    Permission class to check if the user belongs to the 'manager' group.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='manager').exists()


class RequireModule(BasePermission):
    """
    Permission class that checks if a module is enabled.

    Usage:
        class MyView(APIView):
            permission_classes = [IsAuthenticated, RequireModule]
            required_module = Modules.INVENTORY
    """
    def has_permission(self, request, view):
        # Get the required module from the view
        required_module = getattr(view, 'required_module', None)
        print(f"Checking permission for module: {required_module}")

        if not required_module:
            # No module required, allow access
            return True

        # Check if module is enabled
        from apps.common.feature_flags import FeatureFlags

        if not FeatureFlags.is_module_enabled(required_module):
            # Raise a more informative error
            raise PermissionDenied({
                'error': 'Module not enabled',
                'module': required_module,
                'message': f'The {required_module} module is not enabled for your account.',
                'contact': 'Please contact support to enable this feature.'
            })

        return True
