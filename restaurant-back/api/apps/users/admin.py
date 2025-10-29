"""
Django Admin configuration for Users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    Inline Profile editing within User admin.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """
    Extended User admin with Profile inline and custom actions.
    """
    inlines = (ProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'get_groups']
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'groups', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    actions = ['activate_users', 'deactivate_users']
    
    def get_groups(self, obj):
        """Display user groups."""
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Groups'
    
    def activate_users(self, request, queryset):
        """Activate selected users."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} user(s) activated successfully.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} user(s) deactivated successfully.')
    deactivate_users.short_description = "Deactivate selected users"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Profile admin for standalone profile management.
    """
    list_display = ['user', 'location', 'bio_preview']
    search_fields = ['user__username', 'user__email', 'location']
    raw_id_fields = ['user']
    
    def bio_preview(self, obj):
        """Show truncated bio."""
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Bio Preview'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
