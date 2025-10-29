"""
Payment Processing Admin Interface
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for payments."""

    list_display = [
        'paymentID',
        'order_link',
        'amount_display',
        'payment_method_badge',
        'payment_status_badge',
        'processed_by_display',
        'cash_register_display',
        'created_at',
    ]
    list_filter = [
        'payment_method',
        'payment_status',
        'created_at',
        'processed_by',
    ]
    search_fields = [
        'paymentID',
        'order__orderID',
        'transaction_id',
        'processed_by__username',
    ]
    readonly_fields = [
        'paymentID',
        'created_at',
        'updated_at',
    ]
    date_hierarchy = 'created_at'
    autocomplete_fields = ['order', 'cash_register', 'processed_by']

    fieldsets = (
        ('Payment Information', {
            'fields': (
                'paymentID',
                'order',
                'amount',
                'payment_method',
                'payment_status',
            )
        }),
        ('Transaction Details', {
            'fields': (
                'transaction_id',
                'cash_register',
                'processed_by',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def order_link(self, obj):
        """Display order ID as link."""
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:orders_order_change', args=[obj.order.orderID])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.orderID)
    order_link.short_description = 'Order'

    def amount_display(self, obj):
        """Display amount with currency."""
        return format_html('<strong>${}</strong>', f'{obj.amount:.2f}')
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def payment_method_badge(self, obj):
        """Display colored badge for payment method."""
        colors = {
            'CASH': 'green',
            'CREDIT_CARD': 'blue',
            'DEBIT_CARD': 'purple',
            'ONLINE': 'orange',
        }
        color = colors.get(obj.payment_method, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_payment_method_display()
        )
    payment_method_badge.short_description = 'Method'

    def payment_status_badge(self, obj):
        """Display colored badge for payment status."""
        colors = {
            'PENDING': 'orange',
            'COMPLETED': 'green',
            'FAILED': 'red',
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Status'

    def processed_by_display(self, obj):
        """Display user who processed the payment."""
        if obj.processed_by:
            return obj.processed_by.username
        return format_html('<span style="color: gray;">-</span>')
    processed_by_display.short_description = 'Processed By'

    def cash_register_display(self, obj):
        """Display cash register ID if assigned."""
        if obj.cash_register:
            return f"Register #{obj.cash_register.registerID}"
        return format_html('<span style="color: gray;">-</span>')
    cash_register_display.short_description = 'Cash Register'

    actions = ['mark_as_completed', 'mark_as_failed']

    def mark_as_completed(self, request, queryset):
        """Mark selected payments as completed."""
        updated = queryset.update(payment_status='COMPLETED')
        self.message_user(request, f'{updated} payment(s) marked as completed.')
    mark_as_completed.short_description = "Mark as Completed"

    def mark_as_failed(self, request, queryset):
        """Mark selected payments as failed."""
        updated = queryset.update(payment_status='FAILED')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    mark_as_failed.short_description = "Mark as Failed"

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing payments."""
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['order', 'amount', 'payment_method'])
        return readonly

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        totals = queryset.aggregate(
            total_amount=Sum('amount'),
            total_count=Count('paymentID')
        )

        method_totals = {}
        for method, label in Payment.PAYMENT_METHOD_CHOICES:
            amount = queryset.filter(payment_method=method).aggregate(
                total=Sum('amount')
            )['total'] or 0
            method_totals[label] = amount

        status_totals = {}
        for status_code, label in Payment.PAYMENT_STATUS_CHOICES:
            amount = queryset.filter(payment_status=status_code).aggregate(
                total=Sum('amount')
            )['total'] or 0
            status_totals[label] = amount

        extra_context['total_payments'] = totals['total_count'] or 0
        extra_context['total_amount'] = totals['total_amount'] or 0
        extra_context['method_totals'] = method_totals
        extra_context['status_totals'] = status_totals

        return super().changelist_view(request, extra_context=extra_context)
