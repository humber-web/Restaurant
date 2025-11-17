# Restaurant Management System - Features & Functionalities

> **Complete feature documentation for Restaurant Management System**
> Last Updated: 2025-11-15
> System: Django REST Framework (Backend) + Vue.js 3 (Frontend)

---

## Table of Contents

- [Authentication & User Management](#authentication--user-management)
- [Menu Management](#menu-management)
- [Table Management](#table-management)
- [Inventory Management](#inventory-management)
- [Order Management](#order-management)
- [Kitchen Display System](#kitchen-display-system)
- [Payment Processing](#payment-processing)
- [Cash Register Management](#cash-register-management)
- [Dashboard & Analytics](#dashboard--analytics)
- [Accounting & Audit](#accounting--audit)
- [Print Features](#print-features)
- [Real-Time Updates](#real-time-updates)

---

## Authentication & User Management

### User Registration & Login
**Module:** Authentication
**Access Level:** Public (Customer) / Manager (Staff)

**Features:**
- JWT-based authentication with 60-minute access tokens
- Separate registration flows for customers and staff
- Automatic user profile creation
- Role-based permissions (Manager, Staff, Customer)
- User groups management

**Frontend:**
- Route: `/login` - Login interface
- Route: `/configuracoes/utilizadores` - User management (Manager only)

**Backend API:**
- `POST /api/login/` - Authenticate and get JWT token
- `POST /api/register/customer/` - Public customer registration
- `POST /api/register/` - Staff registration (Manager only)
- `GET /api/user/me/` - Get current user details
- `GET /api/user/` - List all users
- `PUT /api/user/<id>/update/` - Update user
- `DELETE /api/user/<id>/delete/` - Delete user
- `GET /api/groups/` - List user groups

**Database Models:**
- User (Django built-in)
- Profile (extends User)

---

## Menu Management

### Menu Categories
**Module:** Configuration
**Access Level:** Manager

**Features:**
- Create, read, update, delete menu categories
- Assign preparation location (Kitchen, Bar, Both)
- Organize menu items by category
- Search and filter categories

**Frontend:**
- Route: `/configuracoes/categorias` - Category management
- Components: CategoriesTableAdvanced, CategoryForm, DeleteCategoryDialog

**Backend API:**
- `POST /api/menu_category/register/` - Create category
- `GET /api/menu_category/` - List all categories
- `GET /api/menu_category/<id>/` - Get category details
- `PUT /api/menu_category/<id>/update/` - Update category
- `DELETE /api/menu_category/<id>/delete/` - Delete category

**Database Models:**
- MenuCategory
  - Fields: categoryID, name, prepared_in ('1'=Kitchen, '2'=Bar, '3'=Both)

### Menu Items (Products)
**Module:** Configuration
**Access Level:** Manager

**Features:**
- Complete product catalog management
- Product descriptions and ingredients
- Price management
- Availability toggle
- Inventory tracking integration
- Auto-availability based on stock
- Advanced search and filtering
- Category assignment

**Frontend:**
- Route: `/configuracoes/produtos` - Product management
- Components: ProductsTableAdvanced, ProductFormDialog, DeleteProductDialog

**Backend API:**
- `POST /api/menu_item/register/` - Create menu item
- `GET /api/menu_item/` - List all menu items
- `GET /api/menu_item/<id>/` - Get item details
- `GET /api/menu_item/search/` - Search menu items
- `PUT /api/menu_item/<id>/update/` - Update menu item
- `DELETE /api/menu_item/<id>/delete/` - Delete menu item
- `GET /api/menu_item/category/` - Get items by category

**Database Models:**
- MenuItem
  - Fields: itemID, name, description, ingredients, price, availability, categoryID, is_quantifiable

---

## Table Management

### Table Configuration
**Module:** Configuration
**Access Level:** Manager/Staff

**Features:**
- Create and manage restaurant tables
- Set table capacity
- Real-time status tracking (Available, Occupied, Reserved)
- Table search functionality
- Auto-status updates based on orders
- Visual status indicators

**Frontend:**
- Route: `/mesas` - Table overview and status
- Route: `/configuracoes/mesas` - Table configuration
- Route: `/mesas/layout` - Visual table layout

**Backend API:**
- `POST /api/table/register/` - Create table
- `GET /api/table/` - List all tables
- `GET /api/table/<id>/` - Get table details
- `GET /api/table/search/` - Search tables
- `PUT /api/table/<id>/update/` - Update table (including status)
- `DELETE /api/table/<id>/delete/` - Delete table

**Database Models:**
- Table
  - Fields: tableid, capacity, status ('AV'=Available, 'OC'=Occupied, 'RE'=Reserved)

### Table Operations View
**Module:** Operations
**Access Level:** Staff

**Features:**
- Grid view of all tables with color-coded status
- Filter by status (All, Available, Occupied, Reserved)
- Search by table number
- Real-time order information for occupied tables
- Table reservation/unreservation
- Quick navigation to table ordering interface
- Time elapsed since order creation
- Order total display

**Frontend:**
- Route: `/mesas` - Main table view
- Real-time WebSocket updates

---

## Inventory Management

### Stock Control
**Module:** Configuration
**Access Level:** Manager

**Features:**
- Track inventory quantities for menu items
- Supplier information management
- Reserved quantity tracking for pending orders
- Oversell quantity support
- Auto-update menu item availability based on stock
- Inventory search and filtering
- Stock alerts

**Frontend:**
- Route: `/configuracoes/inventario` - Inventory management
- Components: InventoryTableAdvanced, InventoryForm, DeleteInventoryDialog

**Backend API:**
- `POST /api/inventory_item/register/` - Create inventory item
- `GET /api/inventory_item/` - List all inventory items
- `GET /api/inventory_item/<id>/` - Get inventory details
- `GET /api/inventory_item/search/` - Search inventory
- `PUT /api/inventory_item/<id>/update/` - Update inventory
- `DELETE /api/inventory_item/<id>/delete/` - Delete inventory item

**Database Models:**
- InventoryItem
  - Fields: itemID, quantity, reserved_quantity, supplier, menu_item, oversell_quantity

---

## Order Management

### Order Creation & Updates
**Module:** Operations
**Access Level:** Staff

**Features:**
- Create new orders for tables or online
- Add/remove items from orders
- Update item quantities
- Order status management (Pending → Preparing → Ready → Delivered → Cancelled)
- Payment status tracking (Pending → Partially Paid → Paid)
- Order type support (Restaurant, Online)
- Auto-calculation of totals with 15% IVA
- Order search and filtering
- Real-time updates across all clients

**Frontend:**
- Route: `/pedidos` - Order dashboard (Kanban/List view)
- Route: `/pedidos/<id>` - Order details
- Route: `/mesas/pedidos?table=<id>` - Table-specific ordering interface
- Components: OrderCard

**Backend API:**
- `POST /api/order/register/` - Create new order
- `GET /api/orders/` - List all orders
- `GET /api/order/<id>/` - Get order details
- `GET /api/order/` - Search orders (by customer, status, payment status, order type, table, date)
- `PUT /api/order/<id>/update/` - Full order replacement
- `PATCH /api/order/<id>/update/` - Partial update (add/remove/update items)
- `DELETE /api/order/<id>/delete/` - Delete order

**Database Models:**
- Order
  - Fields: orderID, customer, status, totalAmount, totalIva, grandTotal, paymentStatus, orderType, last_updated_by, created_at, updated_at
- OrderItem
  - Fields: order, menu_item, quantity, price, to_be_prepared_in, status
- OrderDetails
  - Fields: order, table, online_order_info

### Table Ordering Interface (POS)
**Module:** Point of Sale
**Access Level:** Staff

**Features:**
- Complete ordering system for specific tables
- Menu browsing with category filters
- Product search functionality
- Shopping cart system
- Add items to new or existing orders
- Update item quantities in active orders
- Remove items from orders
- Order transfer between tables
- Order deletion
- Pro-forma receipt printing
- Direct payment navigation
- Real-time order updates
- Item status display (pending, preparing, ready)
- Preparation location indicators (Kitchen/Bar/Store)

**Frontend:**
- Route: `/mesas/pedidos?table=<id>`
- Component: MesasPedidosView.vue
- Components: PrintProforma

### Order Transfer
**Module:** Operations
**Access Level:** Staff

**Features:**
- Transfer all items from one order to another
- Bill splitting support
- Table change functionality
- Auto-merge of duplicate items
- Recalculation of totals
- Source order auto-deletion after transfer

**Backend API:**
- `POST /api/order/transfer/` - Transfer items between orders

### Order Dashboard
**Module:** Operations
**Access Level:** Staff

**Features:**
- Multiple view modes (Kanban board, List view)
- Kanban columns: Pending, Preparing, Ready, Delivered
- Filter by payment status and order type
- Search by order ID or table number
- Statistics cards (total orders, active, pending, preparing, ready)
- Real-time updates via WebSocket
- Order cards with key information
- Quick navigation to order details

**Frontend:**
- Route: `/pedidos`
- Component: PedidosView.vue

---

## Kitchen Display System

### Kitchen Preparation View
**Module:** Kitchen
**Access Level:** Kitchen/Bar Staff

**Features:**
- Station-based order preparation interface
- Station tabs (Cozinha/Bar/Balcão)
- Active orders filtered by preparation station
- Item-level status management
- Quick status updates (Pending → Preparing → Ready → Delivered)
- Time urgency indicators (color-coded by wait time)
- Visual alerts for orders waiting >15/30 minutes
- Statistics per station (total orders, pending, preparing, ready items)
- Kitchen ticket printing per station
- Real-time order updates
- One-click status progression buttons
- Auto-routing of items to correct station based on category

**Frontend:**
- Route: `/cozinha`
- Component: CozinhaView.vue
- Components: PrintKitchenTicket

**Backend API:**
- `PATCH /api/order-item/<id>/status/` - Update item status

**Item Statuses:**
- '1' = Pending
- '2' = Preparing
- '3' = Ready
- '4' = Delivered/Cancelled

---

## Payment Processing

### Payment Processing Interface
**Module:** Payments
**Access Level:** Staff

**Features:**
- Advanced payment interface with item-level selection
- Select specific items to pay (partial payment support)
- Multiple payment methods:
  - Cash
  - Credit Card
  - Debit Card
  - Online
- Manual or item-based amount entry
- Numeric keypad for quick amount entry
- Quick amount buttons (25%, 50%, 75%, 100%)
- Real-time change calculation
- Payment validation (prevents overpayment)
- Receipt printing
- Cash register integration (auto-opens if none available)
- Tracks already-paid items
- Remaining quantity display per item
- Auto-updates order and table status
- Release inventory on successful payment

**Frontend:**
- Route: `/pagamentos/processar?order=<id>`
- Component: PagamentosProcessarView.vue
- Components: PrintReceipt

**Backend API:**
- `POST /api/payment/process/` - Process payment
- `GET /api/payments/` - List all payments
- `GET /api/payment/<id>/` - Get payment details
- `GET /api/payment/` - Search payments (by order, payment method, status, processed by)
- `DELETE /api/payment/<id>/delete/` - Delete payment

**Database Models:**
- Payment
  - Fields: paymentID, order, amount, payment_method, payment_status, transaction_id, cash_register, processed_by, created_at, updated_at
- PaymentItem
  - Fields: payment, order_item, quantity_paid

**Payment Methods:**
- CASH
- CREDIT_CARD
- DEBIT_CARD
- ONLINE

**Payment Status:**
- PENDING
- COMPLETED
- FAILED

### Payment Overview & History
**Module:** Payments
**Access Level:** Staff

**Features:**
- Payment list and overview
- Historical payment records
- Payment reporting
- Filter by date, method, status

**Frontend:**
- Route: `/pagamentos` - Payment overview
- Route: `/pagamentos/historico` - Payment history

---

## Cash Register Management

### Cash Register Sessions
**Module:** Accounting
**Access Level:** Manager

**Features:**
- Open cash register with initial amount
- Live session monitoring
- Transaction breakdown by payment method:
  - Cash
  - Card (Credit/Debit)
  - Transfer
  - Other
  - Check
- Session duration tracking
- Expected cash calculation
- Insert money operation
- Extract money operation (with validation)
- Close register with reconciliation
- Declared vs expected comparison
- Cash difference calculation
- Closing summary dialog
- One open register per user restriction
- Payment integration (requires open register)

**Frontend:**
- Route: `/contabilidade/caixa`
- Component: CaixaRegistadoraView.vue

**Backend API:**
- `POST /api/cash_register/start/` - Start new session
- `POST /api/cash_register/close/` - Close session with reconciliation
- `GET /api/cash_registers/` - List all cash registers
- `GET /api/cash_register/<id>/` - Get cash register details
- `GET /api/cash_register/` - Search cash registers (by user, open status)
- `GET /api/cash_register/summary/` - Get last closed register summary
- `POST /api/cash_register/insert/` - Insert money
- `POST /api/cash_register/extract/` - Extract money

**Database Models:**
- CashRegister
  - Fields: user, initial_amount, final_amount, operations_cash, operations_card, operations_transfer, operations_other, operations_check, start_time, end_time, is_open

---

## Dashboard & Analytics

### Real-Time Dashboard
**Module:** Dashboard
**Access Level:** Staff

**Features:**
- Today's sales revenue and order count
- Active orders breakdown (pending, preparing, ready)
- Table occupancy status
- Monthly revenue
- Last 7 days sales chart
- Top 5 products today
- Recent orders list (last 10)
- Alerts for old orders (>30 min waiting)
- Alerts for high pending order count
- Auto-refresh every 30 seconds
- Real-time updates via WebSocket
- Quick navigation to orders and tables

**Frontend:**
- Route: `/dashboard`
- Component: DashboardView.vue

---

## Accounting & Audit

### Audit Logs
**Module:** Accounting
**Access Level:** Manager

**Features:**
- Automatic logging of all CREATE/UPDATE/DELETE operations
- Operation audit trail
- Activity monitoring
- Filterable log table:
  - By action (CREATE/UPDATE/DELETE)
  - By model
  - By user
  - By date range
- Statistics dashboard:
  - Activity breakdown by action type
  - Unique user count
  - Top 5 most modified models
  - Recent activity (last 24 hours)
- Model-specific filtering
- Comprehensive audit trail

**Frontend:**
- Route: `/contabilidade/auditoria`
- Component: AuditoriaView.vue
- Components: AuditTableAdvanced

**Backend API:**
- `GET /api/audit/logs/` - List operation logs (with filtering)

**Database Models:**
- OperationLog
  - Fields: user, action, content_type, object_id, object_repr, change_message, timestamp

**Implementation:**
- Middleware-based automatic logging (OperationLogMiddleware)
- Tracks user, action type, affected model, object ID
- RequestBodyMiddleware parses JSON for operation logging

### Reports
**Module:** Accounting
**Access Level:** Manager

**Features:**
- Financial and operational reports
- Sales reports
- Revenue analysis

**Frontend:**
- Route: `/contabilidade/relatorios`
- Component: RelatoriosView.vue

---

## Print Features

### Print System
**Module:** Printing
**Access Level:** Staff

**Features:**
- **Pro-forma Receipts** - Preview before payment
  - Component: PrintProforma
  - Shows order details, items, totals
  - Print-friendly formatting

- **Payment Receipts** - After payment confirmation
  - Component: PrintReceipt
  - Shows payment details, items paid, change
  - CVE currency formatting

- **Kitchen Tickets** - Station-specific preparation tickets
  - Component: PrintKitchenTicket
  - Shows items to prepare for specific station
  - Order number, table, time
  - Item quantities and special instructions

**Composable:**
- `usePrint()` - Centralized print management

---

## Real-Time Updates

### WebSocket Integration
**Module:** Real-Time Communication
**Technology:** Django Channels + Redis

**Features:**
- Real-time order updates across all clients
- Push notifications for order changes
- Auto-reconnection on disconnect
- Broadcasting to all connected clients
- Order creation, updates, and status changes

**Backend:**
- WebSocket URL: `ws/orders/`
- Consumer: OrderConsumer (apps/common/consumers.py)
- Backend: Redis (127.0.0.1:6379)

**Frontend:**
- Implemented in: useOrdersStore (Pinia store)
- Used in views:
  - Dashboard
  - Mesas (Tables)
  - Pedidos (Orders)
  - Cozinha (Kitchen)

---

## Technical Specifications

### Frontend Stack
- **Framework:** Vue.js 3 (Composition API)
- **Router:** Vue Router
- **State Management:** Pinia
- **Styling:** Tailwind CSS
- **Icons:** Lucide Vue Next
- **Table Library:** @tanstack/vue-table
- **Build Tool:** Vite

### Backend Stack
- **Framework:** Django REST Framework
- **Authentication:** django-rest-framework-simplejwt
- **Real-Time:** Django Channels + Redis
- **Database:** PostgreSQL
  - Database: restaurant_db
  - User: admin
  - Host: localhost:5432
- **Middleware:**
  - CORS (django-cors-headers)
  - RequestBodyMiddleware (JSON parsing)
  - OperationLogMiddleware (automatic audit logging)

### System Configuration
- **Currency:** CVE (Cape Verdean Escudo)
- **Tax Rate:** 15% IVA (VAT)
- **Language:** Portuguese (Português)
- **JWT Token Lifetime:** 60 minutes
- **WebSocket Auto-Refresh:** 30 seconds (Dashboard)

### Security Features
- JWT-based authentication
- Role-based access control (RBAC)
- Manager-only sensitive operations
- CORS protection
- Automatic audit logging
- User-specific cash register access
- Payment validation
- Inventory protection

### Database Models Summary
1. User & Profile
2. MenuCategory
3. MenuItem
4. InventoryItem
5. Table
6. Order
7. OrderItem
8. OrderDetails
9. Payment
10. PaymentItem
11. CashRegister
12. OperationLog

---

## Navigation Structure

### Main Menu
```
📊 Dashboard (/dashboard)
🪑 Mesas (/mesas)
   └── Layout (/mesas/layout)
   └── Pedidos por Mesa (/mesas/pedidos?table=<id>)
📋 Pedidos (/pedidos)
   └── Detalhes (/pedidos/<id>)
🍳 Cozinha (/cozinha)
💳 Pagamentos
   ├── Processar (/pagamentos/processar?order=<id>)
   ├── Visão Geral (/pagamentos)
   └── Histórico (/pagamentos/historico)
💰 Contabilidade
   ├── Caixa Registadora (/contabilidade/caixa) [Manager]
   ├── Relatórios (/contabilidade/relatorios) [Manager]
   └── Auditoria (/contabilidade/auditoria) [Manager]
⚙️ Configurações [Manager]
   ├── Produtos (/configuracoes/produtos)
   ├── Categorias (/configuracoes/categorias)
   ├── Mesas (/configuracoes/mesas)
   ├── Inventário (/configuracoes/inventario)
   └── Utilizadores (/configuracoes/utilizadores)
```

---

## Summary Statistics

### Total Features Implemented
- **8 Major Modules**
- **25+ Feature Sets**
- **50+ API Endpoints**
- **20+ Frontend Views/Pages**
- **30+ Reusable Components**
- **12 Database Models**
- **Real-Time WebSocket Integration**
- **3 Print Templates**
- **5 Pinia Stores**
- **Complete Audit System**

### Feature Categories
✅ **Authentication & Authorization** - Complete
✅ **Menu Management** - Complete
✅ **Table Management** - Complete with Real-Time
✅ **Inventory Management** - Complete
✅ **Order Management** - Complete with Real-Time
✅ **Kitchen Display System** - Complete with Real-Time
✅ **Payment Processing** - Complete with Multi-Method Support
✅ **Cash Register** - Complete with Reconciliation
✅ **Dashboard & Analytics** - Complete with Real-Time
✅ **Audit & Compliance** - Complete with Auto-Logging
✅ **Print System** - Complete (Receipts, Pro-forma, Kitchen Tickets)
✅ **Real-Time Updates** - WebSocket Integration

---

**Status:** Production-Ready
**Version:** 1.0
**Type:** Full-Stack Restaurant Management & POS System
