from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from .models import StockLog, Notification
from apps.products.models import Product


class InventoryDashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/dashboard.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('stock_qty')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        products = Product.objects.filter(is_active=True)
        ctx['low_stock_products'] = [p for p in products if p.is_low_stock]
        ctx['out_of_stock_products'] = [p for p in products if p.is_out_of_stock]
        ctx['total_products'] = products.count()
        ctx['recent_logs'] = StockLog.objects.select_related('product').all()[:20]
        return ctx


class StockHistoryView(LoginRequiredMixin, ListView):
    model = StockLog
    template_name = 'inventory/stock_history.html'
    context_object_name = 'logs'
    paginate_by = 30

    def get_queryset(self):
        qs = StockLog.objects.select_related('product', 'created_by').all()
        product_id = self.request.GET.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['products'] = Product.objects.filter(is_active=True)
        return ctx


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        if pk:
            Notification.objects.filter(pk=pk).update(is_read=True)
        else:
            Notification.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'inventory/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
