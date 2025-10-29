# Common App

This app contains shared utilities, middleware, permissions, and base classes used across all other Django apps.

## Contents

- **middleware.py**: Request body parsing and operation logging middleware
- **permissions.py**: Custom permission classes (IsManager, etc.)
- **utils.py**: Shared utility functions (IVA calculation, etc.)
- **consumers.py**: WebSocket consumers for real-time features
- **routing.py**: WebSocket URL routing
- **tasks.py**: Background tasks (database listeners, etc.)
- **base_models.py**: Abstract base model classes (if needed)
- **base_serializers.py**: Base serializer classes
- **base_views.py**: Base viewset classes

## Usage

Other apps import from common:
```python
from apps.common.permissions import IsManager
from apps.common.utils import calculate_iva
from apps.common.middleware import RequestBodyMiddleware
```
