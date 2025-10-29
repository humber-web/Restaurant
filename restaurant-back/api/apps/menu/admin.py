"""
Django Admin configuration for Menu app.
"""
from django.contrib import admin
from .models import MenuCategory, MenuItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Menu Categories.
    """
    list_display = ['categoryID', 'name', 'prepared_in', 'item_count']
    list_filter = ['prepared_in']
    search_fields = ['name']
    ordering = ['categoryID']
    
    def item_count(self, obj):
        """Display the number of items in this category."""
        return obj.items.count()
    item_count.short_description = 'Number of Items'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Admin interface for Menu Items with advanced features.
    """
    list_display = ['itemID', 'name', 'categoryID', 'price', 'availability', 'is_quantifiable']
    list_filter = ['availability', 'is_quantifiable', 'categoryID']
    search_fields = ['name', 'description', 'ingredients']
    list_editable = ['availability', 'price']
    ordering = ['itemID']
    actions = ['make_available', 'make_unavailable', 'duplicate_items']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'categoryID', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'availability', 'is_quantifiable')
        }),
        ('Details', {
            'fields': ('ingredients',),
            'classes': ('collapse',)
        }),
    )
    
    def make_available(self, request, queryset):
        """Mark selected items as available."""
        count = queryset.update(availability=True)
        self.message_user(request, f'{count} item(s) marked as available.')
    make_available.short_description = "Mark selected items as available"
    
    def make_unavailable(self, request, queryset):
        """Mark selected items as unavailable."""
        count = queryset.update(availability=False)
        self.message_user(request, f'{count} item(s) marked as unavailable.')
    make_unavailable.short_description = "Mark selected items as unavailable"
    
    def duplicate_items(self, request, queryset):
        """Duplicate selected menu items."""
        count = 0
        for item in queryset:
            item.pk = None  # Create new instance
            item.name = f"{item.name} (Copy)"
            item.save()
            count += 1
        self.message_user(request, f'{count} item(s) duplicated successfully.')
    duplicate_items.short_description = "Duplicate selected items"
