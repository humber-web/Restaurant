"""
Audit and Operation Logging Admin Interface
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing operation logs.
    Read-only - logs cannot be edited or deleted.
    """

    list_display = [
        'timestamp',
        'user_display',
        'action_badge',
        'content_type',
        'object_id',
        'object_repr_short',
    ]
    list_filter = [
        'action',
        'content_type',
        'timestamp',
        'user',
    ]
    search_fields = [
        'user__username',
        'object_repr',
        'change_message',
    ]
    readonly_fields = [
        'user',
        'action',
        'content_type',
        'object_id',
        'object_repr',
        'change_message',
        'timestamp',
    ]
    date_hierarchy = 'timestamp'

    # Make it read-only
    def has_add_permission(self, request):
        """Disable adding logs manually."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow viewing but not editing."""
        return True

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Action Details', {
            'fields': ('action', 'content_type', 'object_id', 'object_repr')
        }),
        ('Change Description', {
            'fields': ('change_message',)
        }),
    )

    def user_display(self, obj):
        """Display username."""
        return obj.user.username
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'

    def action_badge(self, obj):
        """Display colored badge for action type."""
        colors = {
            'CREATE': 'green',
            'UPDATE': 'blue',
            'DELETE': 'red',
        }
        color = colors.get(obj.action, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.action
        )
    action_badge.short_description = 'Action'
    action_badge.admin_order_field = 'action'

    def object_repr_short(self, obj):
        """Display shortened object representation."""
        if len(obj.object_repr) > 50:
            return obj.object_repr[:50] + '...'
        return obj.object_repr
    object_repr_short.short_description = 'Object'
