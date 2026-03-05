from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.billing.models import Invoice
from apps.services.models import ServiceRecord
from apps.purchases.models import Supplier
from apps.inventory.models import StockLog, Notification
from .serializers import (
    UserSerializer, ProductSerializer, CategorySerializer,
    InvoiceSerializer, ServiceRecordSerializer, SupplierSerializer,
    StockLogSerializer, NotificationSerializer,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(is_superuser=False)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'barcode']
    filterset_fields = ['category', 'is_active']

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        products = [p for p in self.get_queryset() if p.is_low_stock or p.is_out_of_stock]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invoice.objects.select_related('created_by').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['invoice_number', 'customer_name', 'vehicle_number']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ServiceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ServiceRecord.objects.select_related('service_type', 'mechanic').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['vehicle_number', 'customer_name']
    filterset_fields = ['status', 'mechanic']

    @action(detail=False, methods=['get'], url_path='by-vehicle')
    def by_vehicle(self, request):
        vehicle = request.query_params.get('vehicle', '')
        qs = self.get_queryset().filter(vehicle_number__iexact=vehicle)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Supplier.objects.all()


class StockLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = StockLog.objects.select_related('product').all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'change_type']


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all marked read'})
