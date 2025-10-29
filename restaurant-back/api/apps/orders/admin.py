"""
Order Management Admin Interface
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Order, OrderItem, OrderDetails


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 1
    readonly_fields = ['price', 'to_be_prepared_in']
    fields = ['menu_item', 'quantity', 'price', 'status', 'to_be_prepared_in']
    autocomplete_fields = ['menu_item']


class OrderDetailsInline(admin.StackedInline):
    """Inline admin for order details."""
    model = OrderDetails
    can_delete = False
    fields = ['table', 'online_order_info']
    autocomplete_fields = ['table']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders."""

    list_display = [
        'orderID',
        'customer_display',
        'order_type_badge',
        'status_badge',
        'payment_status_badge',
        'item_count',
        'grand_total_display',
        'table_display',
        'created_at',
    ]
    list_filter = [
        'status',
        'paymentStatus',
        'orderType',
        'created_at',
    ]
    search_fields = [
        'orderID',
        'customer__username',
        'customer__email',
        'details__table__tableid',
    ]
    readonly_fields = [
        'orderID',
        'totalAmount',
        'totalIva',
        'grandTotal',
        'created_at',
        'updated_at',
        'last_updated_by'
    ]
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, OrderDetailsInline]

    fieldsets = (
        ('Order Information', {
            'fields': (
                'orderID',
                'customer',
                'orderType',
                'status',
                'paymentStatus'
            )
        }),
        ('Totals', {
            'fields': (
                'totalAmount',
                'totalIva',
                'grandTotal'
            )
        }),
        ('Metadata', {
            'fields': (
                'last_updated_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def customer_display(self, obj):
        """Display customer name or 'Guest'."""
        if obj.customer:
            return obj.customer.username
        return format_html('<span style="color: gray;">Guest</span>')
    customer_display.short_description = 'Customer'

    def order_type_badge(self, obj):
        """Display colored badge for order type."""
        colors = {
            'RESTAURANT': 'blue',
            'ONLINE': 'green',
        }
        color = colors.get(obj.orderType, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.orderType
        )
    order_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        """Display colored badge for order status."""
        colors = {
            'PENDING': 'orange',
            'PREPARING': 'blue',
            'READY': 'green',
            'DELIVERED': 'gray',
            'CANCELLED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_status_badge(self, obj):
        """Display colored badge for payment status."""
        colors = {
            'PENDING': 'orange',
            'PARTIALLY_PAID': 'blue',
            'PAID': 'green',
            'FAILED': 'red',
        }
        color = colors.get(obj.paymentStatus, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_paymentStatus_display()
        )
    payment_status_badge.short_description = 'Payment'

    def item_count(self, obj):
        """Display number of items in order."""
        count = obj.items.count()
        return format_html('<strong>{}</strong> items', count)
    item_count.short_description = 'Items'

    def grand_total_display(self, obj):
        """Display grand total with currency."""
        return format_html('<strong>${}</strong>', f'{obj.grandTotal:.2f}')
    grand_total_display.short_description = 'Total'
    grand_total_display.admin_order_field = 'grandTotal'

    def table_display(self, obj):
        """Display table number if assigned."""
        if hasattr(obj, 'details') and obj.details.table:
            return f"Table {obj.details.table.tableid}"
        return format_html('<span style="color: gray;">-</span>')
    table_display.short_description = 'Table'

    actions = [
        'mark_as_preparing',
        'mark_as_ready',
        'mark_as_delivered',
        'mark_as_cancelled'
    ]

    def mark_as_preparing(self, request, queryset):
        """Mark selected orders as preparing."""
        updated = queryset.update(status='PREPARING')
        self.message_user(request, f'{updated} order(s) marked as preparing.')
    mark_as_preparing.short_description = "Mark as Preparing"

    def mark_as_ready(self, request, queryset):
        """Mark selected orders as ready."""
        updated = queryset.update(status='READY')
        self.message_user(request, f'{updated} order(s) marked as ready.')
    mark_as_ready.short_description = "Mark as Ready"

    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered."""
        updated = queryset.update(status='DELIVERED')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark as Delivered"

    def mark_as_cancelled(self, request, queryset):
        """Mark selected orders as cancelled."""
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} order(s) cancelled.')
    mark_as_cancelled.short_description = "Cancel Orders"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for order items."""

    list_display = [
        'id',
        'order_id_display',
        'menu_item',
        'quantity',
        'price_display',
        'status_badge',
        'preparation_location'
    ]
    list_filter = ['status', 'to_be_prepared_in']
    search_fields = [
        'order__orderID',
        'menu_item__name'
    ]
    readonly_fields = ['price', 'to_be_prepared_in']

    def order_id_display(self, obj):
        """Display order ID as link."""
        return f"Order #{obj.order.orderID}"
    order_id_display.short_description = 'Order'

    def price_display(self, obj):
        """Display price with currency."""
        return f"${obj.price:.2f}"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'

    def status_badge(self, obj):
        """Display colored badge for item status."""
        status_map = {
            '1': ('Pending', 'orange'),
            '2': ('Preparing', 'blue'),
            '3': ('Ready', 'green'),
            '4': ('Cancelled', 'red'),
        }
        label, color = status_map.get(obj.status, ('Unknown', 'gray'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            label
        )
    status_badge.short_description = 'Status'

    def preparation_location(self, obj):
        """Display preparation location."""
        locations = {
            '1': ('Kitchen', 'red'),
            '2': ('Bar', 'blue'),
            '3': ('Both', 'purple'),
        }
        label, color = locations.get(obj.to_be_prepared_in, ('Unknown', 'gray'))
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )
    preparation_location.short_description = 'Prep Location'


@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    """Admin interface for order details."""

    list_display = [
        'id',
        'order_id_display',
        'table_display',
        'has_online_info'
    ]
    search_fields = [
        'order__orderID',
        'table__tableid',
        'online_order_info'
    ]
    autocomplete_fields = ['table']

    def order_id_display(self, obj):
        """Display order ID."""
        return f"Order #{obj.order.orderID}"
    order_id_display.short_description = 'Order'

    def table_display(self, obj):
        """Display table number."""
        if obj.table:
            return f"Table {obj.table.tableid}"
        return format_html('<span style="color: gray;">No table</span>')
    table_display.short_description = 'Table'

    def has_online_info(self, obj):
        """Display if online order info exists."""
        if obj.online_order_info:
            return format_html('<span style="color: green;"> Yes</span>')
        return format_html('<span style="color: gray;"> No</span>')
    has_online_info.short_description = 'Online Info'
