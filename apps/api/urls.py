from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, InvoiceViewSet,
    ServiceRecordViewSet, SupplierViewSet, StockLogViewSet,
    NotificationViewSet, UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'services', ServiceRecordViewSet, basename='service')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'stock-logs', StockLogViewSet, basename='stocklog')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='api_token'),
    path('', include(router.urls)),
]
