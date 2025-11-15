# Restaurant Real-Time Application Startup Guide

This guide explains how to run the restaurant application with **real-time WebSocket support** for instant order updates across all devices.

## Prerequisites

- **Python 3.11+**
- **PostgreSQL** running with `restaurant_db` database
- **Redis** server (for WebSocket channel layer)
- **Node.js** and npm (for Vue frontend)

## Architecture

The application uses **ASGI (Asynchronous Server Gateway Interface)** instead of traditional WSGI to support WebSocket connections for real-time updates:

- **WSGI** (old): HTTP only, no real-time
- **ASGI** (current): HTTP + WebSocket, real-time updates ✅

## Installation

### 1. Install Python Dependencies

```bash
cd restaurant-back/api
pip install -r requirements.txt
```

**Key packages for real-time:**
- `channels` - Django WebSocket support
- `channels-redis` - Redis backend for Channels
- `daphne` - ASGI server (replaces traditional WSGI server)

### 2. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
```

**macOS:**
```bash
brew install redis
```

**Check Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Install Frontend Dependencies

```bash
cd restaurant-front-2
npm install
```

## Running the Application (3 Services)

You need **three terminals** running simultaneously:

### Terminal 1: Redis Server

```bash
redis-server
```

**Expected output:**
```
* Ready to accept connections
```

**Default:** `127.0.0.1:6379`

### Terminal 2: Django Backend with ASGI (Daphne)

```bash
cd restaurant-back/api
daphne -b 0.0.0.0 -p 8000 api.asgi:application
```

**Alternative with verbose logging:**
```bash
daphne -v 2 -b 0.0.0.0 -p 8000 api.asgi:application
```

**Expected output:**
```
INFO     Starting server at tcp:port=8000:interface=0.0.0.0
INFO     HTTP/2 support enabled
INFO     Configuring endpoint tcp:port=8000:interface=0.0.0.0
```

**IMPORTANT:** Do NOT use `python3 manage.py runserver` - it uses WSGI and does not support WebSockets!

### Terminal 3: Vue Frontend

```bash
cd restaurant-front-2
npm run serve
```

**Expected output:**
```
App running at:
- Local:   http://localhost:8080/
```

## Verifying Real-Time Functionality

### 1. Check WebSocket Connection

Open browser console (F12) and navigate to the application. You should see:

```
WebSocket connection established
Order update received: {...}
```

### 2. Test Real-Time Updates

**Test 1 - Multiple Browsers:**
1. Open the application in two different browsers
2. Create/update an order in Browser A
3. Browser B should see the update instantly (< 1 second)

**Test 2 - Tables View:**
1. Open "Mesas" (Tables) view
2. In another browser, add items to a table's order
3. The table card should update automatically showing the new total

**Test 3 - Order Management:**
1. Open a table's order management page
2. In another browser/device, modify that same order
3. The page should update automatically without refresh

### 3. Monitor WebSocket Traffic

**Backend (Daphne terminal):**
```
WebSocket HANDSHAKING /ws/orders/ [127.0.0.1:xxxxx]
WebSocket CONNECT /ws/orders/ [127.0.0.1:xxxxx]
```

**Frontend (Browser Console):**
```javascript
// When order is created/updated
Order update received: {
  type: 'order_update',
  order: { orderID: 123, ... }
}
```

## Troubleshooting

### WebSocket Not Connecting

**Problem:** Browser console shows WebSocket connection failed

**Solutions:**
1. Verify Redis is running: `redis-cli ping`
2. Check you're using Daphne (not `manage.py runserver`)
3. Check CORS settings in `settings.py` include your frontend URL
4. Verify backend is on `http://localhost:8000` (or update WebSocket URL in frontend)

### Orders Not Updating in Real-Time

**Problem:** Changes don't appear automatically

**Solutions:**
1. Check browser console for WebSocket errors
2. Verify `ordersStore.initWebSocket()` is called in the view
3. Check Redis is running and accessible
4. Restart Daphne server

### Redis Connection Error

**Problem:** `ConnectionRefusedError: [Errno 111] Connection refused`

**Solution:**
```bash
# Start Redis
redis-server

# Or check if it's already running
redis-cli ping
```

### Port Already in Use

**Problem:** `Error: [Errno 98] Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
daphne -b 0.0.0.0 -p 8001 api.asgi:application
```

## Configuration Files

### Backend - settings.py

```python
# ASGI Configuration (Required for WebSockets)
ASGI_APPLICATION = 'api.asgi.application'

# Channel Layers (Redis Backend)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)]
        },
    },
}
```

### Backend - asgi.py

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### Frontend - WebSocket Connection

```typescript
// src/services/websocket/orders.ts
const ws = new WebSocket('ws://localhost:8000/ws/orders/')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // Handle order updates
}
```

## Production Deployment

For production, use a process manager:

**Option 1: Supervisor**
```ini
[program:daphne]
command=/path/to/venv/bin/daphne -b 0.0.0.0 -p 8000 api.asgi:application
directory=/path/to/restaurant-back/api
autostart=true
autorestart=true
```

**Option 2: systemd**
```ini
[Unit]
Description=Daphne ASGI Server
After=network.target

[Service]
ExecStart=/path/to/venv/bin/daphne -b 0.0.0.0 -p 8000 api.asgi:application
WorkingDirectory=/path/to/restaurant-back/api
Restart=always

[Install]
WantedBy=multi-user.target
```

## Development vs Production

### Development (Current Setup)
- Daphne directly on port 8000
- No SSL/TLS (ws://)
- Single worker

### Production (Recommended)
- Nginx reverse proxy
- SSL/TLS (wss://)
- Multiple Daphne workers
- Redis Sentinel for high availability

## Quick Reference

| Service | Command | Port | Protocol |
|---------|---------|------|----------|
| Redis | `redis-server` | 6379 | TCP |
| Backend | `daphne -b 0.0.0.0 -p 8000 api.asgi:application` | 8000 | HTTP + WebSocket |
| Frontend | `npm run serve` | 8080 | HTTP |

## WebSocket Endpoints

- **Orders**: `ws://localhost:8000/ws/orders/`
  - Real-time order create/update/delete notifications
  - Broadcasts to all connected clients
  - Updates MesasView and MesasPedidosView automatically

## Benefits of Real-Time System

✅ **Instant Updates**: See changes in < 1 second
✅ **Multi-Device Sync**: All terminals stay synchronized
✅ **Better UX**: No manual refresh needed
✅ **Kitchen Efficiency**: Orders appear instantly on kitchen display
✅ **Lower Server Load**: No constant polling (30s/15s intervals removed)
✅ **Scalable**: WebSocket connections more efficient than HTTP polling

---

**Need Help?**
- Check logs in Daphne terminal
- Monitor Redis: `redis-cli monitor`
- Browser DevTools → Network → WS (WebSocket tab)
