"""
Table Management URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('table/register/', views.CreateTableView.as_view(), name='table-create'),
    path('table/', views.TableListView.as_view(), name='table-list'),
    path('table/<int:pk>/', views.TableDetailView.as_view(), name='table-detail'),
    path('table/search/', views.TableDetailView.as_view(), name='table-search'),
    path('table/<int:pk>/update/', views.TableUpdateView.as_view(), name='table-update'),
    path('table/<int:pk>/delete/', views.TableDeleteView.as_view(), name='table-delete'),
]
