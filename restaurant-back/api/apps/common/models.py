"""
Common models for cross-cutting concerns.
"""
from django.db import models
from django.core.exceptions import ValidationError


class ModuleSubscription(models.Model):
    """
    Track which modules are enabled for the organization.
    This allows per-organization module licensing.
    """
    module_name = models.CharField(max_length=50, unique=True, db_index=True)
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave blank for no expiration")

    # Billing information
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes about this subscription")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_common_module_subscription'
        ordering = ['module_name']
        verbose_name = 'Module Subscription'
        verbose_name_plural = 'Module Subscriptions'

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.module_name} - {status}"

    def clean(self):
        """Validate module dependencies before enabling."""
        from apps.common.feature_flags import FeatureFlags, PREMIUM_MODULES, FREE_MODULES

        if self.is_enabled and self.module_name in PREMIUM_MODULES:
            # Check if required modules are enabled
            satisfied, missing = FeatureFlags.check_dependencies(self.module_name)
            if not satisfied:
                raise ValidationError(
                    f"Cannot enable {self.module_name}. Missing required modules: {', '.join(missing)}"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
