"""
User Management URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.CreateUserView.as_view(), name='user-register'),
    path('register/customer/', views.CreateCustomerView.as_view(), name='customer-register'),
    path('login/', views.LoginView.as_view(), name='login'),
    
    # User Management
    path('user/', views.UserListView.as_view(), name='user-list'),
    path('user/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('user/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('user/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    
    # Profiles & Groups
    path('profile/', views.ProfileView.as_view(), name='profile-list'),
    path('groups/', views.GroupListView.as_view(), name='group-list'),
]
