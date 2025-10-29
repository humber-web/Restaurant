"""
Menu Management URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Menu Categories
    path('menu_category/register/', views.CreateMenuCategoryView.as_view(), name='menu-category-create'),
    path('menu_category/', views.MenuCategoryListView.as_view(), name='menu-category-list'),
    path('menu_category/<int:pk>/', views.MenuCategoryDetailView.as_view(), name='menu-category-detail'),
    path('menu_category/<int:pk>/update/', views.MenuCategoryUpdateView.as_view(), name='menu-category-update'),
    path('menu_category/<int:pk>/delete/', views.MenuCategoryDeleteView.as_view(), name='menu-category-delete'),
    
    # Menu Items
    path('menu_item/register/', views.CreateMenuItemView.as_view(), name='menu-item-create'),
    path('menu_item/', views.MenuItemListView.as_view(), name='menu-item-list'),
    path('menu_item/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('menu_item/search/', views.MenuItemDetailView.as_view(), name='menu-item-search'),
    path('menu_item/<int:pk>/update/', views.MenuItemUpdateView.as_view(), name='menu-item-update'),
    path('menu_item/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menu-item-delete'),
    path('menu_item/category/', views.MenuItemCategoryListView.as_view(), name='menu-item-by-category'),
]
