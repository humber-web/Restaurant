"""
Cash Register Management Admin Interface
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import CashRegister


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    """Admin interface for cash registers."""

    list_display = [
        'id',
        'user_display',
        'status_badge',
        'initial_amount_display',
        'final_amount_display',
        'cash_operations_display',
        'card_operations_display',
        'session_duration',
        'start_time',
    ]
    list_filter = [
        'is_open',
        'start_time',
        'user',
    ]
    search_fields = [
        'user__username',
        'user__email',
    ]
    readonly_fields = [
        'start_time',
        'end_time',
        'total_operations',
        'session_duration_display',
    ]
    date_hierarchy = 'start_time'

    fieldsets = (
        ('Session Information', {
            'fields': (
                'user',
                'is_open',
                'start_time',
                'end_time',
                'session_duration_display',
            )
        }),
        ('Cash Amounts', {
            'fields': (
                'initial_amount',
                'final_amount',
            )
        }),
        ('Operations by Payment Method', {
            'fields': (
                'operations_cash',
                'operations_card',
                'operations_transfer',
                'operations_check',
                'operations_other',
                'total_operations',
            )
        }),
    )

    def user_display(self, obj):
        """Display user name."""
        return obj.user.username
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'

    def status_badge(self, obj):
        """Display colored badge for register status."""
        if obj.is_open:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">OPEN</span>'
            )
        else:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">CLOSED</span>'
            )
    status_badge.short_description = 'Status'

    def initial_amount_display(self, obj):
        """Display initial amount with currency."""
        return format_html('<span style="color: blue;">${}</span>', f'{obj.initial_amount:.2f}')
    initial_amount_display.short_description = 'Initial'
    initial_amount_display.admin_order_field = 'initial_amount'

    def final_amount_display(self, obj):
        """Display final amount with currency."""
        if obj.final_amount is not None:
            color = 'green' if obj.final_amount >= obj.initial_amount else 'red'
            return format_html(
                '<strong style="color: {};">${}</strong>',
                color,
                f'{obj.final_amount:.2f}'
            )
        return format_html('<span style="color: gray;">-</span>')
    final_amount_display.short_description = 'Final'
    final_amount_display.admin_order_field = 'final_amount'

    def cash_operations_display(self, obj):
        """Display cash operations total."""
        return format_html('${}', f'{obj.operations_cash:.2f}')
    cash_operations_display.short_description = 'Cash'
    cash_operations_display.admin_order_field = 'operations_cash'

    def card_operations_display(self, obj):
        """Display card operations total."""
        return format_html('${}', f'{obj.operations_card:.2f}')
    card_operations_display.short_description = 'Card'
    card_operations_display.admin_order_field = 'operations_card'

    def total_operations(self, obj):
        """Calculate total operations."""
        total = (
            obj.operations_cash +
            obj.operations_card +
            obj.operations_transfer +
            obj.operations_check +
            obj.operations_other
        )
        return format_html('<strong>${}</strong>', f'{total:.2f}')
    total_operations.short_description = 'Total Operations'

    def session_duration(self, obj):
        """Calculate and display session duration."""
        if obj.end_time:
            duration = obj.end_time - obj.start_time
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f}h"
        return format_html('<span style="color: green;">Active</span>')
    session_duration.short_description = 'Duration'

    def session_duration_display(self, obj):
        """Detailed session duration for detail view."""
        if obj.end_time:
            duration = obj.end_time - obj.start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "Session still open"
    session_duration_display.short_description = 'Session Duration'

    actions = ['close_selected_registers']

    def close_selected_registers(self, request, queryset):
        """Close selected open registers."""
        open_registers = queryset.filter(is_open=True)
        count = 0
        for register in open_registers:
            register.close_register(
                declared_cash=register.initial_amount + register.operations_cash,
                declared_card=register.operations_card
            )
            count += 1
        self.message_user(request, f'{count} cash register(s) closed.')
    close_selected_registers.short_description = "Close selected registers"

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing registers."""
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['user', 'initial_amount'])
        return readonly

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        open_registers = queryset.filter(is_open=True)
        closed_registers = queryset.filter(is_open=False)

        open_totals = open_registers.aggregate(
            total_cash=Sum('operations_cash'),
            total_card=Sum('operations_card'),
            count=Sum('id')
        )

        closed_totals = closed_registers.aggregate(
            total_cash=Sum('operations_cash'),
            total_card=Sum('operations_card'),
            count=Sum('id')
        )

        extra_context['open_registers_count'] = open_registers.count()
        extra_context['open_registers_cash'] = open_totals['total_cash'] or 0
        extra_context['open_registers_card'] = open_totals['total_card'] or 0

        extra_context['closed_registers_count'] = closed_registers.count()
        extra_context['closed_registers_cash'] = closed_totals['total_cash'] or 0
        extra_context['closed_registers_card'] = closed_totals['total_card'] or 0

        return super().changelist_view(request, extra_context=extra_context)
