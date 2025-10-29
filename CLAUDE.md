# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack restaurant management system with a Django REST Framework backend and Vue.js frontend. The system manages orders, menus, inventory, tables, payments, and cash registers with real-time order updates via WebSockets.

## Repository Structure

```
/Restaurant
├── restaurant-back/      # Django backend
│   ├── api/             # Django project root
│   │   ├── api/         # Project settings and URLs
│   │   └── core/        # Main application
│   └── venv/            # Python virtual environment
└── frontend/            # Vue.js frontend
    └── src/
```

## Backend (Django REST Framework)

### Running the Backend

**Activate virtual environment:**
```bash
cd restaurant-back
source venv/bin/activate
```

**Run development server:**
```bash
cd restaurant-back/api
python3 manage.py runserver
```

**Common Django commands:**
```bash
# Make migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Run Django shell
python3 manage.py shell
```

### Database Configuration

- **Database:** PostgreSQL
- **Database name:** restaurant_db
- **User:** admin
- **Password:** admin123
- **Host:** localhost:5432

### External Dependencies

- **Redis:** Required for WebSocket support (Django Channels)
  - Default host: 127.0.0.1:6379
  - Used for real-time order updates

### Architecture

**Core App Structure** ([restaurant-back/api/core/](restaurant-back/api/core/)):

Models are split into separate files in [core/models/](restaurant-back/api/core/models/):
- `user_models.py` - User profiles
- `menu_category_models.py` - Menu categories
- `menu_item_models.py` - Menu items
- `inventory_item_models1.py` - Inventory (note: uses InventoryItemN model)
- `table_models.py` - Restaurant tables
- `order_models.py` - Orders
- `order_item_models.py` - Order line items
- `order_details_models.py` - Order metadata
- `payment_models.py` - Payments
- `cash_register_models.py` - Cash register sessions
- `historyc_models.py` - Operation logging

Views are organized by domain in [core/Views/](restaurant-back/api/core/Views/) (note capital 'V'):
- `user_views.py` - User CRUD and authentication
- `auth_views.py` - Login and customer registration
- `menu_category_views.py` - Menu category management
- `menu_item_views.py` - Menu item management
- `inventory_item_views.py` - Inventory management
- `table_views.py` - Table management
- `order_views.py` - Order creation, updates, transfers
- `payment_views.py` - Payment processing
- `insert_extract_money_views.py` - Cash register transactions
- `cash_register_views.py` - Open/close cash register

**Key files:**
- [core/serializers.py](restaurant-back/api/core/serializers.py) - All DRF serializers
- [core/middleware.py](restaurant-back/api/core/middleware.py) - Custom middleware for request body parsing and operation logging
- [core/consumers.py](restaurant-back/api/core/consumers.py) - WebSocket consumer for real-time order updates
- [core/routing.py](restaurant-back/api/core/routing.py) - WebSocket URL routing

**Key Settings** ([api/settings.py](restaurant-back/api/api/settings.py:1)):
- JWT authentication via django-rest-framework-simplejwt (60 min access token lifetime)
- CORS configured for local development IPs
- Custom middleware: RequestBodyMiddleware parses JSON for operation logging
- Custom middleware: OperationLogMiddleware logs CREATE/UPDATE operations to OperationLog model
- WebSocket support via Django Channels with Redis backend

### API Structure

All API endpoints are prefixed with `/api/`. See [api/urls.py](restaurant-back/api/api/urls.py:1) for complete endpoint list.

**Key endpoint patterns:**
- `/api/register/` - User registration
- `/api/login/` - JWT authentication
- `/api/{resource}/` - List resources
- `/api/{resource}/register` - Create resource
- `/api/{resource}/<pk>/` - Get resource detail
- `/api/{resource}/<pk>/update/` - Update resource
- `/api/{resource}/<pk>/delete/` - Delete resource
- `/api/order/transfer/` - Transfer order items between orders
- `/api/cash_register/{action}/` - Cash register operations
- `ws/orders/` - WebSocket for real-time order updates

### Operation Logging

POST/PUT requests automatically log operations to the OperationLog model when the request body contains:
- `model` - Model name (lowercase)
- `operation` - Either "CREATE" or "UPDATE"
- `object_id` - The object ID being operated on

## Frontend (Vue.js 3)

### Running the Frontend

```bash
cd frontend
npm run serve
```

### Building for Production

```bash
cd frontend
npm run build
```

### Architecture

**Tech Stack:**
- Vue 3 with Composition API
- Vue Router for routing
- Tailwind CSS for styling
- FontAwesome icons

**Views** ([frontend/src/views/](frontend/src/views/)):
- `HomeView.vue` - Main layout with nested routes
- `DashboardView.vue` - Dashboard page
- `MenuView.vue` - Customer-facing menu (standalone route)
- `OrderView.vue` - Order management (Spanish: "pedidos")
- `ProductsView.vue` - Product management (Spanish: "productos")

**Routing** ([frontend/src/router/index.js](frontend/src/router/index.js:1)):
- `/` - Home layout
  - `/dashboard` - Dashboard
  - `/pedidos` - Orders
  - `/productos` - Products
- `/menu` - Customer menu (standalone)

## Development Notes

### Backend Development

- Python virtual environment is located at `restaurant-back/venv/`
- Always activate venv before running Django commands
- Use `python3` (not `python`) for all Python commands
- The core app uses a split models pattern - each domain has its own model file
- Views directory uses capital 'V': `core/Views/`
- WebSocket functionality requires Redis to be running

### Frontend Development

- Components and views use Spanish terminology for some routes (pedidos, productos)
- Tailwind CSS is configured via [tailwind.config.js](frontend/tailwind.config.js)
- Vue CLI service is used for development and builds

### CORS Configuration

Backend CORS is configured for specific local IPs in [api/settings.py](restaurant-back/api/api/settings.py:67). When adding new frontend servers, update:
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
