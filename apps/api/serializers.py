from rest_framework import serializers
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.billing.models import Invoice, InvoiceItem
from apps.services.models import ServiceRecord
from apps.purchases.models import Supplier
from apps.inventory.models import StockLog, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'phone']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'image', 'selling_price',
                  'purchase_price', 'stock_qty', 'low_stock_limit', 'unit', 'barcode',
                  'is_active', 'is_low_stock', 'is_out_of_stock']


class InvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'customer_name', 'customer_phone', 'vehicle_number',
                  'service_charge', 'discount', 'gst_percent', 'subtotal', 'gst_amount',
                  'grand_total', 'payment_method', 'notes', 'created_by_name', 'created_at', 'items']
        read_only_fields = ['invoice_number', 'subtotal', 'gst_amount', 'grand_total']


class ServiceRecordSerializer(serializers.ModelSerializer):
    mechanic_name = serializers.CharField(source='mechanic.get_full_name', read_only=True)
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)

    class Meta:
        model = ServiceRecord
        fields = ['id', 'vehicle_number', 'vehicle_model', 'customer_name', 'customer_phone',
                  'service_type', 'service_type_name', 'mechanic', 'mechanic_name', 'status',
                  'checklist', 'notes', 'estimated_amount', 'created_at', 'completed_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'phone', 'email', 'address', 'gst_number', 'is_active']


class StockLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockLog
        fields = ['id', 'product', 'product_name', 'change_type', 'quantity_change',
                  'stock_before', 'stock_after', 'note', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'notification_type', 'is_read', 'created_at']
