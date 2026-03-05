from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.http import JsonResponse
from django.views import View
import json
from datetime import timedelta
from apps.billing.models import Invoice, InvoiceItem
from apps.products.models import Product
from apps.services.models import ServiceRecord
from apps.inventory.models import Notification


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        this_month_start = today.replace(day=1)

        # Today's sales
        today_invoices = Invoice.objects.filter(created_at__date=today)
        ctx['today_sales_count'] = today_invoices.count()
        ctx['today_revenue'] = today_invoices.aggregate(t=Sum('grand_total'))['t'] or 0

        # Monthly revenue
        month_invoices = Invoice.objects.filter(created_at__date__gte=this_month_start)
        ctx['monthly_revenue'] = month_invoices.aggregate(t=Sum('grand_total'))['t'] or 0
        ctx['monthly_invoice_count'] = month_invoices.count()

        # Stock alerts
        all_products = Product.objects.filter(is_active=True)
        ctx['low_stock_count'] = sum(1 for p in all_products if p.is_low_stock)
        ctx['out_of_stock_count'] = sum(1 for p in all_products if p.is_out_of_stock)
        ctx['low_stock_products'] = [p for p in all_products if p.is_low_stock or p.is_out_of_stock][:5]

        # Pending services
        ctx['pending_services'] = ServiceRecord.objects.filter(status__in=['PENDING', 'IN_PROGRESS']).count()
        ctx['recent_services'] = ServiceRecord.objects.select_related('mechanic').filter(
            status__in=['PENDING', 'IN_PROGRESS']
        )[:5]

        # Recent invoices
        ctx['recent_invoices'] = Invoice.objects.select_related('created_by').all()[:5]

        # Total products
        ctx['total_products'] = all_products.count()

        # Last 7 days sales for chart
        chart_labels = []
        chart_data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            rev = Invoice.objects.filter(created_at__date=d).aggregate(t=Sum('grand_total'))['t'] or 0
            chart_labels.append(d.strftime('%d %b'))
            chart_data.append(float(rev))

        ctx['chart_labels'] = json.dumps(chart_labels)
        ctx['chart_data'] = json.dumps(chart_data)
        return ctx


class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/sales_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        today = timezone.now().date()

        if not date_from:
            date_from = today.replace(day=1).isoformat()
        if not date_to:
            date_to = today.isoformat()

        invoices = Invoice.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).select_related('created_by')

        total_revenue = invoices.aggregate(t=Sum('grand_total'))['t'] or 0
        total_invoices = invoices.count()
        ctx['invoices'] = invoices
        ctx['total_revenue'] = total_revenue
        ctx['total_invoices'] = total_invoices
        ctx['avg_invoice_value'] = round(total_revenue / total_invoices, 2) if total_invoices else 0
        ctx['date_from'] = date_from
        ctx['date_to'] = date_to
        return ctx


class ProductSalesReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/product_sales_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        today = timezone.now().date()

        if not date_from:
            date_from = today.replace(day=1).isoformat()
        if not date_to:
            date_to = today.isoformat()

        product_sales = InvoiceItem.objects.filter(
            invoice__created_at__date__gte=date_from,
            invoice__created_at__date__lte=date_to
        ).values('product__name').annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_revenue')

        ctx['product_sales'] = product_sales
        ctx['date_from'] = date_from
        ctx['date_to'] = date_to
        return ctx


class ProfitReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/profit_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        today = timezone.now().date()

        if not date_from:
            date_from = today.replace(day=1).isoformat()
        if not date_to:
            date_to = today.isoformat()

        items = InvoiceItem.objects.filter(
            invoice__created_at__date__gte=date_from,
            invoice__created_at__date__lte=date_to
        ).select_related('product')

        total_revenue = sum(i.total_price for i in items)
        total_cost = sum(i.product.purchase_price * i.quantity for i in items)
        gross_profit = total_revenue - total_cost

        ctx.update({
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'gross_profit': gross_profit,
            'date_from': date_from,
            'date_to': date_to,
        })
        return ctx


class ChartDataAPIView(LoginRequiredMixin, View):
    """JSON API endpoint for dashboard charts."""
    def get(self, request):
        today = timezone.now().date()
        chart_labels = []
        chart_data = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            rev = Invoice.objects.filter(created_at__date=d).aggregate(t=Sum('grand_total'))['t'] or 0
            chart_labels.append(d.strftime('%d %b'))
            chart_data.append(float(rev))
        return JsonResponse({'labels': chart_labels, 'data': chart_data})
