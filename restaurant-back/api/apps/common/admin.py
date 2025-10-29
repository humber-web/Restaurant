"""
Admin interface for common models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from apps.common.models import ModuleSubscription
from apps.common.feature_flags import PREMIUM_MODULES, FREE_MODULES


@admin.register(ModuleSubscription)
class ModuleSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for managing module subscriptions."""

    list_display = [
        'module_name',
        'status_indicator',
        'monthly_price_display',
        'expiration_status',
        'enabled_at',
        'updated_at'
    ]
    list_filter = ['is_enabled', 'module_name']
    search_fields = ['module_name', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'enabled_at']

    fieldsets = (
        ('Module Information', {
            'fields': ('module_name', 'is_enabled')
        }),
        ('Billing', {
            'fields': ('monthly_price', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('notes', 'enabled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_indicator(self, obj):
        """Display colored status indicator."""
        if obj.is_enabled:
            if obj.expires_at and obj.expires_at < timezone.now():
                return format_html(
                    '<span style="color: orange;">⚠️ Expired</span>'
                )
            return format_html(
                '<span style="color: green;">✅ Active</span>'
            )
        return format_html(
            '<span style="color: red;">❌ Disabled</span>'
        )
    status_indicator.short_description = 'Status'

    def monthly_price_display(self, obj):
        """Display monthly price with currency."""
        if obj.monthly_price == 0:
            return format_html('<span style="color: green;">Free</span>')
        return f"${obj.monthly_price}/month"
    monthly_price_display.short_description = 'Price'

    def expiration_status(self, obj):
        """Display expiration status."""
        if not obj.expires_at:
            return format_html('<span style="color: green;">No expiration</span>')

        if obj.expires_at < timezone.now():
            return format_html(
                '<span style="color: red;">Expired {}</span>',
                obj.expires_at.strftime('%Y-%m-%d')
            )

        days_left = (obj.expires_at - timezone.now()).days
        if days_left <= 7:
            color = 'orange'
        else:
            color = 'green'

        return format_html(
            '<span style="color: {};">Expires {} ({} days)</span>',
            color,
            obj.expires_at.strftime('%Y-%m-%d'),
            days_left
        )
    expiration_status.short_description = 'Expiration'

    actions = ['enable_modules', 'disable_modules']

    def enable_modules(self, request, queryset):
        """Bulk enable modules."""
        updated = queryset.update(is_enabled=True)
        self.message_user(request, f'{updated} module(s) enabled successfully.')
    enable_modules.short_description = "Enable selected modules"

    def disable_modules(self, request, queryset):
        """Bulk disable modules."""
        updated = queryset.update(is_enabled=False)
        self.message_user(request, f'{updated} module(s) disabled successfully.')
    disable_modules.short_description = "Disable selected modules"

    def get_form(self, request, obj=None, **kwargs):
        """Customize form with help text."""
        form = super().get_form(request, obj, **kwargs)

        # Add help text for module_name field
        module_choices = []
        module_choices.append(('', '--- Select Module ---'))

        # Add free modules
        for module in FREE_MODULES:
            module_choices.append((module, f'{module.upper()} (Free)'))

        # Add premium modules
        for module, info in PREMIUM_MODULES.items():
            price = info['price']
            module_choices.append((module, f'{module.upper()} - {info["name"]} (${price}/mo)'))

        form.base_fields['module_name'].help_text = (
            'Select the module to manage. Premium modules require payment.'
        )

        return form
