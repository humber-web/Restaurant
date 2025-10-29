"""
Django Admin configuration for Tables app.
"""
from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """
    Admin interface for Restaurant Tables.
    """
    list_display = ['tableid', 'capacity', 'status', 'status_icon']
    list_filter = ['status', 'capacity']
    search_fields = ['tableid']
    list_editable = ['status']
    ordering = ['tableid']
    actions = ['mark_available', 'mark_occupied', 'mark_reserved']
    
    fieldsets = (
        ('Table Information', {
            'fields': ('capacity', 'status')
        }),
    )
    
    def status_icon(self, obj):
        """Display a colored icon for table status."""
        icons = {
            'AV': '🟢',  # Available - Green
            'OC': '🔴',  # Occupied - Red
            'RE': '🟡',  # Reserved - Yellow
        }
        return f"{icons.get(obj.status, '⚪')} {obj.get_status_display()}"
    status_icon.short_description = 'Status'
    
    def mark_available(self, request, queryset):
        """Mark selected tables as available."""
        count = queryset.update(status='AV')
        self.message_user(request, f'{count} table(s) marked as available.')
    mark_available.short_description = "Mark selected tables as Available"
    
    def mark_occupied(self, request, queryset):
        """Mark selected tables as occupied."""
        count = queryset.update(status='OC')
        self.message_user(request, f'{count} table(s) marked as occupied.')
    mark_occupied.short_description = "Mark selected tables as Occupied"
    
    def mark_reserved(self, request, queryset):
        """Mark selected tables as reserved."""
        count = queryset.update(status='RE')
        self.message_user(request, f'{count} table(s) marked as reserved.')
    mark_reserved.short_description = "Mark selected tables as Reserved"
