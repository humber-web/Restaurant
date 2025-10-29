"""
Menu Management Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from apps.common.permissions import IsManager
from apps.audit.models import OperationLog
from .models import MenuCategory, MenuItem
from .serializers import MenuCategorySerializer, MenuItemSerializer


# ==================== MENU CATEGORY VIEWS ====================

class CreateMenuCategoryView(APIView):
    """
    Create a new menu category.
    POST /api/menu_category/register/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = MenuCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            # Update request body for operation logging
            if hasattr(request, 'body_data'):
                request.body_data['object_id'] = category.categoryID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuCategoryListView(APIView):
    """
    List all menu categories.
    GET /api/menu_category/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = MenuCategory.objects.all().order_by('categoryID')
        serializer = MenuCategorySerializer(categories, many=True)
        return Response(serializer.data)


class MenuCategoryDetailView(APIView):
    """
    Get menu category details.
    GET /api/menu_category/<pk>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        category = get_object_or_404(MenuCategory, pk=pk)
        serializer = MenuCategorySerializer(category)
        return Response(serializer.data)


class MenuCategoryUpdateView(APIView):
    """
    Update a menu category.
    PUT /api/menu_category/<pk>/update/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        category = get_object_or_404(MenuCategory, pk=pk)
        serializer = MenuCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuCategoryDeleteView(APIView):
    """
    Delete a menu category.
    DELETE /api/menu_category/<pk>/delete/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        category = get_object_or_404(MenuCategory, pk=pk)
        content_type = ContentType.objects.get_for_model(category)
        
        # Log delete operation
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=category.categoryID,
            object_repr=f"menucategory {category.categoryID}",
            change_message=f"User {request.user} performed DELETE on menucategory {category.categoryID}"
        )
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== MENU ITEM VIEWS ====================

class CreateMenuItemView(APIView):
    """
    Create a new menu item.
    POST /api/menu_item/register/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body for operation logging
            if hasattr(request, 'body_data'):
                request.body_data['object_id'] = item.itemID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemListView(APIView):
    """
    List all menu items.
    GET /api/menu_item/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = MenuItem.objects.all().order_by('itemID')
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)


class MenuItemDetailView(APIView):
    """
    Get menu item details or search by name/category.
    GET /api/menu_item/<pk>/ - Get by ID
    GET /api/menu_item/search/?name=...&categoryName=... - Search
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        # If a primary key is provided, fetch by ID
        if pk:
            try:
                item = MenuItem.objects.get(pk=pk)
                serializer = MenuItemSerializer(item)
                return Response(serializer.data)
            except MenuItem.DoesNotExist:
                raise Http404
        
        # Otherwise, search by query parameters
        item_name = request.query_params.get('name')
        category_name = request.query_params.get('categoryName')
        queryset = MenuItem.objects.all()

        if item_name:
            queryset = queryset.filter(name__icontains=item_name)
        if category_name:
            queryset = queryset.filter(categoryID__name__icontains=category_name)

        if not queryset.exists():
            raise Http404

        serializer = MenuItemSerializer(queryset, many=True)
        return Response(serializer.data)


class MenuItemUpdateView(APIView):
    """
    Update a menu item.
    PUT /api/menu_item/<pk>/update/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDeleteView(APIView):
    """
    Delete a menu item.
    DELETE /api/menu_item/<pk>/delete/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk)
        content_type = ContentType.objects.get_for_model(item)
        
        # Log delete operation
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=item.itemID,
            object_repr=f"menuitem {item.itemID}",
            change_message=f"User {request.user} performed DELETE on menuitem {item.itemID}"
        )
        
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MenuItemCategoryListView(APIView):
    """
    Get menu items grouped by category.
    GET /api/menu_item/category/
    Returns: List of categories with their items
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = []
        
        # Add "All" category
        all_items = MenuItem.objects.all()
        categories.append({
            'name': 'Todas',
            'total': all_items.count(),
            'items': MenuItemSerializer(all_items, many=True).data
        })
        
        # Add each category with its items
        for category in MenuCategory.objects.all():
            items = MenuItem.objects.filter(categoryID=category)
            categories.append({
                'name': category.name,
                'total': items.count(),
                'items': MenuItemSerializer(items, many=True).data
            })
        
        return Response(categories)
