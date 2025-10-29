"""
User Management Models
"""
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    User profile extending Django's User model with additional fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'apps_profile'  # Use existing table from apps app
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
